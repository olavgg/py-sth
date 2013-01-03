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

from conf import LOG

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
                    "number_of_shards": 2,
                    "number_of_replicas": 1,
                    "store": {
                        #"type": "memory",
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
                        'parent': {
                            'type': 'string', 'index': 'not_analyzed'
                        },
                        'path': {
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
                        'path': {
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
            
    def index_folders(self):
        pass
        
    def index_files(self):
        pass