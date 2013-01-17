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

Created on Dec 11, 2012

@Author: Olav Groenaas Gjerde
'''
import os
import datetime
from urllib import quote_plus as uenc

from domain.user import User
from domain.file import File
from domain.folder import Folder
from services.shell_command import ShellCommand
from services.es_service import EsService
from services.task_service import TaskService

from conf.base import Base
from conf import LOG

DATEFORMAT = '%Y-%m-%d %H:%M'

class UserDataService(object):
    ''' Find and index data for a user '''
    
    def __init__(self, user):
        '''Constructor'''
        if isinstance(user, User) and isinstance(user.uid, str):
            base = Base.get_instance()
            self.__syspath = base.app.config['USER_HOME_PATH']
            self.__path = "{path}/{uid}".format(
                path=self.__syspath,
                uid=user.uid
            )
            self.__user = user
            self.__es_service = EsService.get_instance()
            self.__es_node_path = (
                '{idx_name}/node/_bulk'.format(idx_name=user.uid))
        else:
            raise TypeError('argument must be of type User')
    
    @property
    def es_service(self):
        ''' Get ElasticSearch service instance '''
        return self.__es_service
    
    @property
    def es_node_path(self):
        ''' Get ElasticSearch node url '''
        return self.__es_node_path
    
    @property
    def user(self):
        ''' Get user '''
        return self.__user
    
    @property
    def path(self):
        ''' Get path '''
        return self.__path
    
    @path.setter
    def path(self, value):
        ''' Set path '''
        self.__path = value
        
    @property
    def syspath(self):
        ''' Get full system path '''
        return self.__syspath
    
    @syspath.setter
    def syspath(self, value):
        ''' Set full system path '''
        self.__syspath = value
    
    def find_all_folders(self):
        ''' Find all folders for user '''
        cmd = ('ls -Ra {path} '
               '| grep -e "./.*:" | sed "s/://;s/\/home//"').format(
            path = self.path
        )
        LOG.debug(cmd)
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            splitted_path = line.split('/')
            folder = splitted_path[len(splitted_path)-1]
            parent_folder = line[:-(len(folder)+1)]
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(self.syspath+line)).strftime(DATEFORMAT)
            data = {'name':folder,'parent':parent_folder,
                'path':line,'date_modified':date_modified}
            folders.append(data)
        return folders
    
    def find_folder_files(self, folder):
        ''' Find all files for given folder '''
        cmd = 'find "{path}" -maxdepth 1 -type f | sed "s#.*/##"'.format(
            path = self.syspath + folder['path']
        )
        results = ShellCommand(cmd).run()
        files = []
        for line in results[0]:
            path = '{folder}/{file}'.format(folder=folder['path'],file=line)
            fullpath = self.syspath+path
            size = UserDataService.sizeof_fmt(os.path.getsize(fullpath))
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(fullpath)).strftime(DATEFORMAT)
            data = {
                'name':line,'folder':folder['path'],'path':path,
                'size':size, 'date_modified':date_modified
            }
            files.append(data)
        return files
    
    def index_folders_and_files(self):
        '''
        Uses the FolderService to find all folders for the user. Path to
        the folder is urlencoded and assigned as a id for the Folder type
        in the ElasticSearch index.
        '''
        items_indexed = 0
        folders = self.find_all_folders()
        folder_bulk = []
        for folder in folders:
            index_id = uenc(folder['path'])
            parent = uenc(folder['parent'])
            folder_bulk.append({'index' : {'_id':index_id}})
            data = {
                'name':folder['name'],
                'parent':parent,
                'date_modified':folder['date_modified'],
                'type':'folder',
                'size':''
            }
            folder_bulk.append(data)
            items_indexed += self.index_files(folder)
        self.es_service.bulk_insert(self.es_node_path,folder_bulk)
        items_indexed += len(folders)
        return items_indexed
    
    def index_files(self, folder):
        ''' Index the files in folder '''
        folder_files = self.find_folder_files(folder)
        file_bulk = []
        for file_obj in folder_files:
            file_index_id = uenc(file_obj['path'])
            folder_index_id = uenc(file_obj['folder'])
            file_bulk.append({'index' : {'_id':file_index_id}})
            fdata = {
                'name':file_obj['name'],
                'parent':folder_index_id,
                'date_modified':file_obj['date_modified'],
                'size':file_obj['size'],
                'type':'file'
            }
            file_bulk.append(fdata)
        if len(file_bulk) > 0:
            self.es_service.bulk_insert(self.es_node_path,file_bulk)
        return len(file_bulk)
        
    def build_index(self):
        ''' 
        Build a new index, steps involved are:
        Create/Overwrite index
        Add folders to index
        Add files to index
        Flush index when done
        '''
        LOG.debug(u'Start building index for {uid}'.format(uid=self.user.uid))
        result = self.es_service.create_index(
            self.user.uid, data=self.get_index_metadata(), overwrite=True)
        if result['status'] != 200:
            LOG.error(str(result))
            LOG.error(u'An error occured while creating the index')
            return False
        items_indexed = self.index_folders_and_files()
        result = self.es_service.conn.post(
            '{idx_name}/_flush'.format(idx_name=self.user.uid))
        if result['status'] != 200:
            LOG.error(str(result))
            LOG.error(u'An error occured when executing an index flush')
            return False
        msg = u'Indexed {total} items for user {uid}.'.format(
            total=items_indexed,
            uid=self.user.uid
        )
        LOG.debug(msg)
    
    def get_index_metadata(self):
        ''' 
        Metadata index for a user
        Compress ratio is about 2.0 for this kind of data.
        
        One replica and two shards should be good enough for this use case.
        That's why it's hard coded for now.
        '''
        return {
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
                'node': {
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
                        },
                        'type': {
                            'type': 'string', 'index': 'not_analyzed'
                        },
                        'size': {
                            'type': 'string', 'index': 'not_analyzed'
                        }
                    }
                }
            }
        }
        
    def do_full_sync(self):
        '''
        Do a full sync of the user filesystem. Find all folders from the
        user's filesystem and fetch all the folders in user's index. Compare
        them, find the NEW and DELETED folders. This will also work with
        renamed folders.
        
        When all folders are compared and properly index then walk through
        each folder and compare its files with the files in the index.
        '''
        search_url = '{idx_name}/_search'.format(idx_name=self.user.uid)
        results = self.es_service.conn.get(search_url,data={
            "from": 0,
            "size": 999999999,
            "fields": [],
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "type": "folder"
                        }
                    }]
                }
            }
        })['hits']['hits']
        results = {doc['_id']:doc for doc in results}
        disk_folders = self.find_all_folders()
        disk_folders = (
            {uenc(folder['path']):folder for folder in disk_folders})
        es_folders = set(results.keys())
        folders = set(disk_folders.keys())
        deleted_docs = es_folders - folders
        new_docs = folders - es_folders
        print deleted_docs
        """
        for doc_to_delete in deleted_docs:
            del_url = '{idx_name}/node/{id}'.format(
                idx_name=self.user.uid,
                id=doc_to_delete)
            result = self.es_service.conn.delete(del_url)
            print result
        """
        print new_docs
        for new_document in new_docs:
            folder = disk_folders[new_document]
            parent = uenc(folder['parent'])
            put_url = '{idx_name}/node/{id}'.format(
                idx_name=self.user.uid,
                id=new_document)
            print put_url
            result = self.es_service.conn.put(put_url,data={
                'name':folder['name'],
                'parent':parent,
                'date_modified':folder['date_modified'],
                'size':'',
                'type':'folder'
            })
            print result
    
    def do_folder_sync(self, folder):
        '''
        Pass a folder, read it from disk and the ES index. Compare its folders
        and files and return the correct results based what is stored on disk.
        '''
        if isinstance(folder, Folder):
            index_id = uenc(folder)
    
    @staticmethod
    def index_all_users():
        ''' Static method for indexing all folders and files for all users '''
        users = User.get_users()
        for user in users:
            try:
                TaskService(build_process, user=user)
            except ValueError, error:
                LOG.error(error)
        return len(users)
        
    @staticmethod
    def sizeof_fmt(num):
        ''' Byte representation'''
        for x in [' bytes','KB','MB','GB']:
            if num < 1024.0 and num > -1024.0:
                if x == ' bytes':
                    return "%3i%s" % (num, x)
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

def build_process(values):
    ''' Task/process function '''
    user = values.get('user')
    if user:
        service = UserDataService(user)
        service.build_index()