'''
Copyright (C) <2012> <Olav Groenaas Gjerde>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on Dec 30, 2012

@Author: Olav Groenaas Gjerde
'''

from external_projects import rawes
from requests import ConnectionError
import json
import urllib

from conf import LOG
from services.folder_service import FolderService

class EsService(object):
    ''' Handles connecting to a ElasticSearch cluster and data manipulation '''

    def __init__(self):
        ''' 
        Hard coded connection for now. Elasticsearch supports loadbalancing 
        with the option to set node.data to false. Read more on
        www.elasticsearch.org/guide/reference/modules/node.html
        '''
        try:
            es_server = 'es01:9200'
            self.conn = rawes.Elastic(es_server)
            if self.conn == None:
                es_server = 'es02:9200'
                self.conn = rawes.Elastic(es_server)
                if self.conn == None:
                    raise ConnectionError("Couldn't connect to %s"%(es_server))
        except ConnectionError as err:
            LOG.exception(str(err))
            
    def get_status(self):
        return self.conn.get('')
            
    def create_index(self, name, overwrite=False):
        ''' 
        Create index for user, overwrite if a second argument with value true 
        is added. Compress ratio is about 2.0 for this kind of data.
        
        One replica and two shards should be good enough for this use case.
        That's why it's hard coded for now.
        '''
        if overwrite:
            idx_exists = self.conn.head(name)
            if idx_exists:
                self.conn.delete(name)
        result = self.conn.put(name, data={
            "settings": {
                "index": {
                    "refresh_interval" : "60s",
                    "number_of_shards": 2,
                    "number_of_replicas": 1,
                    "store": {
                        "type": "niofs",
                        "compress": {"stored": 'true',"tv": 'true'}
                    },
                    "gateway": { "type" : "none" }
                    #"cache.field.type" : "soft"
                },
            },
            "mappings": {
                'folder': {
                    "_source": { "compress": "true" },
                    "_all" : {"enabled" : False},
                    'properties': {
                        'name': {
                            'type': 'string', 'index': 'analyzed'
                        },
                        'date_modified': {
                            'type': 'date', 
                            'format':'yyyy-MM-dd HH:mm', 
                            'index': 'not_analyzed'
                        },
                        'parent': {
                            'type': 'string', 'index': 'not_analyzed'
                        }
                    }
                },
                'file': {
                    'properties': {
                        'name': {
                            'type': 'string', 'index': 'analyzed'
                        },
                        'folder': {
                            'type': 'string', 'index': 'not_analyzed'
                        },
                        'date_modified': {
                            'type': 'date', 
                            'format':'yyyy-MM-dd HH:mm', 
                            'index': 'not_analyzed'
                        },
                        'size': {
                            'type': 'string', 'index': 'not_analyzed'
                        }
                    }
                }
            }
        })
        if result['status'] != 200:
            LOG.error("Couldn't create index")
        return result
    
    def bulk_insert(self, path, data, bulk_size=8000):
        ''' 
        Bulk insert data to elasticsearch, default size of bulk_size is 8000
        '''
        counter = 0
        dbuf = []
        for item in data:
            if counter == bulk_size:
                self.__do_bulk_insert(path, dbuf)
                counter = 0
                dbuf = []
            dbuf.append(item)
            counter += 1
        self.__do_bulk_insert(path, dbuf)
            
    def __do_bulk_insert(self, path, databulk):
        ''' Private function that does the actual bulk insert to ES '''
        bdata = '\n'.join([json.dumps(bdat) for bdat in databulk])+'\n'
        result = self.conn.post(path, data=bdata)
        if result['status'] != 200:
            LOG.error(str(result))
            LOG.error(bdata)
            LOG.error("Couldn't do bulk insert")
            
    def index_folders_and_files(self, user):
        '''
        Uses the FolderService to find all folders for the user. Path to
        the folder is urlencoded and assigned as a id for the Folder type
        in the ElasticSearch index.
        '''
        folder_path = '{idx_name}/folder/_bulk'.format(idx_name=user.uid)
        file_path = '{idx_name}/file/_bulk'.format(idx_name=user.uid)
        items_indexed = 0
        fservice = FolderService(user)
        folders = fservice.find_all()
        folder_bulk = []
        for folder in folders:
            index_id = urllib.quote_plus(folder['path'])
            folder_bulk.append({'index' : {'_id':index_id}})
            data = {
                'name':folder['name'],
                'parent':folder['parent'],
                'date_modified':folder['date_modified']
            }
            folder_bulk.append(data)
            folder_files = fservice.find_folder_files(folder)
            file_bulk = []
            for file_obj in folder_files:
                file_index_id = urllib.quote_plus(file_obj['path'])
                folder_index_id = urllib.quote_plus(file_obj['folder'])
                file_bulk.append({'index' : {'_id':file_index_id}})
                fdata = {
                    'name':file_obj['name'],
                    'folder':folder_index_id,
                    'date_modified':file_obj['date_modified']
                }
                file_bulk.append(fdata)
            if len(file_bulk) > 0:
                self.bulk_insert(file_path,file_bulk)
                items_indexed += len(file_bulk)
        self.bulk_insert(folder_path,folder_bulk)
        items_indexed += len(folders)
        return items_indexed
        
    
    def build_index(self, user):
        ''' 
        Build a new index, steps involved are:
        Create/Overwrite index
        Add folders to index
        Add files to index
        Flush index when done
        '''
        LOG.debug(u'Start building index for {uid}'.format(uid=user.uid))
        result = self.create_index(user.uid, overwrite=True)
        if result['status'] != 200:
            LOG.error(str(result))
            LOG.error(u'An error occured while creating the index')
            return False
        items_indexed = self.index_folders_and_files(user)
        result = self.conn.post('{idx_name}/_flush'.format(idx_name=user.uid))
        if result['status'] != 200:
            LOG.error(str(result))
            LOG.error(u'An error occured when executing an index flush')
            return False
        msg = u'Indexed {total} items for user {uid}.'.format(
            total=items_indexed,
            uid=user.uid
        )
        LOG.debug(msg)
        return dict(items_indexed=items_indexed)