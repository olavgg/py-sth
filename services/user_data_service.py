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

from flask import current_app as app

from domain.user import User
from domain.node import Node
from domain.folder import Folder
from services.shell_command import ShellCommand
from services.es_service import EsService
from services.task_service import TaskService

class UserDataService(object):
    ''' Find and index data for a user '''
    
    def __init__(self, user):
        '''Constructor'''
        if isinstance(user, User) and (
                isinstance(user.uid, str) or isinstance(user.uid, unicode)):
            self.__syspath = app.config['USER_HOME_PATH']
            self.__path = u"{path}/{uid}".format(
                path=self.__syspath,
                uid=user.uid
            )
            self.__user = user
            self.__es_service = EsService.get_instance()
            self.__bulk_insert_url = u'{uid}/node/_bulk'.format(uid=user.uid)
            self.__settings_url = u'{uid}/_settings'.format(uid = user.uid)
            self.__count_url = u'{uid}/node/_search?search_type=count'.format(
                uid=user.uid)
        else:
            raise TypeError('argument must be of type User')
    
    @property
    def es_service(self):
        ''' Get ElasticSearch service instance '''
        return self.__es_service
    
    @property
    def bulk_insert_url(self):
        ''' Get bulk insert url '''
        return self.__bulk_insert_url
    
    @property
    def settings_url(self):
        ''' Get settings url '''
        return self.__settings_url
    
    @property
    def count_url(self):
        ''' Get count url '''
        return self.__count_url
    
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
    
    def find_all_folders(self, folder=None):
        ''' Find all folders for user, do not return symlinks '''
        if folder == None:
            cmd = u'find "{path}" -type d | sed "s#{syspath}##"'.format(
                path = self.path,
                syspath = self.syspath
            )
        else:
            if isinstance(folder, Folder):
                cmd = u'find "{path}" -type d | sed "s#{syspath}##"'.format(
                    path = folder.sys_path,
                    syspath = self.syspath
                )
            else:
                raise TypeError(u'folder is not of type domain.folder.Folder')
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            line = unicode(line, 'utf8')
            app.logger.info(type(line))
            app.logger.info(line)
            try:
                fullpath = (self.syspath+line).encode('utf-8')
                if os.path.islink(fullpath):
                    continue
            except Exception, e:
                app.logger.error(str(e))
                app.logger.info(type(line))
                app.logger.info(line)
                app.logger.info(line.encode('utf-8'))
                fullpath = (self.syspath+line).encode('utf-8')
            splitted_path = line.split('/')
            folder = splitted_path[len(splitted_path)-1]
            parent_folder = line[:-(len(folder)+1)]
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(fullpath)).strftime(
                    app.config['DATEFORMAT'])
            data = {'name':folder, 'parent':parent_folder,
                'path':line,'date_modified':date_modified}
            folders.append(data)
        return folders
    
    def find_folder_folders(self, folder):
        ''' Find all folders for given folder, but do not return symlinks '''
        cmd = u'find "{path}" -maxdepth 1 -type d | sed "s#.*/##"'.format(
            path = folder.sys_path
        )
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            line = unicode(line, 'utf8')
            if os.path.islink(self.syspath+line):
                continue
            path = u'{folder}/{file}'.format(folder=folder.path, file=line)
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(folder.sys_path)).strftime(
                    app.config['DATEFORMAT'])
            data = {
                'name':line,'parent':folder.path,'path':path,
                'date_modified':date_modified
            }
            folders.append(data)
        return folders
    
    def index_folders_and_files(self, folder=None):
        '''
        Find all folders for the user. Path to the folder is urlencoded and
        assigned as a id for the Folder type in the ElasticSearch index.
        '''
        items_indexed = 0
        folders = self.find_all_folders(folder)
        folder_bulk = []
        for folder in folders:
            index_id = uenc(folder['path'].encode('utf-8'))
            parent = uenc(folder['parent'].encode('utf-8'))
            folder_bulk.append({'index' : {'_id':index_id}})
            data = {
                'name':folder['name'],
                'parent':parent,
                'date_modified':folder['date_modified'],
                'type':Node.FOLDER_TYPE,
                'size':''
            }
            folder_bulk.append(data)
            items_indexed += self.index_files(folder)
        self.es_service.bulk_insert(self.bulk_insert_url, folder_bulk)
        items_indexed += len(folders)
        return items_indexed
    
    def index_files(self, folder):
        ''' Index the files in folder '''
        folder_instance = Folder.get_instance(folder['path'])
        folder_files = folder_instance.files
        file_bulk = []
        for file_obj in folder_files:
            file_bulk.append({'index' : {'_id':file_obj.index_id}})
            fdata = {
                'name':file_obj.name,
                'parent':folder_instance.index_id,
                'date_modified':file_obj.date_modified,
                'size':file_obj.get_size(),
                'type':file_obj.type
            }
            file_bulk.append(fdata)
        if len(file_bulk) > 0:
            self.es_service.bulk_insert(self.bulk_insert_url, file_bulk)
        return len(file_bulk)
        
    def build_index(self):
        ''' 
        Build a new index, steps involved are:
        Create/Overwrite index
        Add folders to index
        Add files to index
        Flush index when done
        '''
        app.logger.debug(u'Start building index for {uid}'.format(uid=self.user.uid))
        result = self.es_service.create_index(
            self.user.uid, data=self.get_index_metadata(), overwrite=True)
        if result['status'] != 200:
            app.logger.error(str(result))
            app.logger.error(u'An error occured while creating the index')
            return False
        items_indexed = self.index_folders_and_files()
        msg = u'Indexed {total} items for user {uid}.'.format(
            total=items_indexed,
            uid = self.user.uid
        )
        max_seg_url = '{uid}/_optimize?max_num_segments=4'.format(
            uid = self.user.uid)
        self.es_service.conn.post(max_seg_url, data={})
        self.es_service.conn.put(self.settings_url, data={
            "index": {
                "number_of_replicas": 1,
                "refresh_interval" : "1s"
            }
        })
        self.optimize_index()
        self.flush_index()
        app.logger.info(msg)
    
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
                            'type': 'string', 'index': 'not_analyzed'
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
    def find_by_parent_id(self, parent_id):
        ''' Return document ids by parent id '''
        max_size = int(self.es_service.conn.get(self.count_url, data={
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "parent": parent_id
                        }
                    }]
                }
            }
        })['hits']['total'])
        query_url = '{idx_name}/node/_search'.format(idx_name=self.user.uid)
        results = self.es_service.conn.get(query_url,data={
            "from": 0,
            "size": max_size,
            "fields": [],
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "parent": parent_id
                        }
                    }]
                }
            }
        })
        if results['status'] != 200:
            return list()
        return [ doc['_id'] for doc in results['hits']['hits'] ]
        
    def delete_document_by_parent_id(self, document_id):
        ''' 
        Deletes documents from ES by id string argument, delete nodes
        that has the id as parent. 
        '''
        ids_to_delete = self.find_by_parent_id(document_id)
        del_url = '{idx_name}/node/_query'.format(idx_name=self.user.uid)
        result = self.es_service.conn.delete(del_url, data={
            "term" : { "parent" : document_id }
        })
        if result['status'] != 200:
            error_msg = (
                u'Couldn\'t delete documents by parent: {doc}').format(
                    doc=document_id)
            app.logger.error(error_msg)
        return ids_to_delete
        
    def delete_document_by_id(self, document_id):
        ''' Deletes documents from ES by id string argument '''
        del_url = '{idx_name}/node/{id}'.format(
            idx_name=self.user.uid,
            id=uenc(document_id)) # dual url encoding as ES decodes it
        result = self.es_service.conn.delete(del_url)
        if result['status'] != 200:
            error_msg = u'Couldn\'t delete document: {doc} from ES'.format(
                doc=del_url
            )
            app.logger.error(error_msg)
        else:
            return document_id
            
    def index_document_by_node(self, node):
        ''' Index a node by supplying a node argument '''
        if isinstance(node, Node):
            if node.type == Node.FILE_TYPE:
                size = node.get_size()
            else:
                size = ''
            put_url = '{idx_name}/node/{id}'.format(
                idx_name=self.user.uid,
                # dual url encoding as ES decodes it
                id=uenc(uenc(node.path.encode('utf-8'))))
            data={
                'name':node.name,
                'parent':uenc(node.get_parent()),
                'date_modified':node.date_modified,
                'size':size,
                'type':node.type
            }
            result = self.es_service.conn.put(put_url, data=data)
            if result['status'] != 201:
                error_msg = u'Couldn\'t index document: {doc} to ES'.format(
                    doc=node.path
                )
                app.logger.error(error_msg)
            else:
                app.logger.debug(u'Indexed {name}'.format(name=node.name))
        else:
            raise TypeError(u'node is not of type domain.node.Node')
    
    def do_folder_sync(self, node_id):
        '''
        Pass a folder_id, read it from disk and the ES index. Compare its
        content and files and return the correct results based what is stored
        on disk.
        
        We do two queries, first to find total hits and then use total hits
        to do the second query. The reason for this is that a huge size value
        decrease Elasticsearch query performance by a huge margin.
        '''
        folder = Folder.get_instance(node_id, decode=True)
        if folder:
            index_id = uenc(folder.path.encode('utf-8'))
            max_size = int(self.es_service.conn.get(self.count_url,data={
                "query": {
                    "bool": {
                        "must": [{
                            "term": {
                                "parent": index_id
                            }
                        }]
                    }
                }
            })['hits']['total'])
            search_url = u'{idx_name}/node/_search'.format(
                idx_name=self.user.uid)
            results = self.es_service.conn.get(search_url,data={
                "from": 0,
                "size": max_size,
                "fields": [],
                "query": {
                    "bool": {
                        "must": [{
                            "term": {
                                "parent": index_id
                            }
                        }]
                    }
                }
            })
            es_node_ids = set([doc['_id'] for doc in results['hits']['hits']])
            disk_nodes = {node.index_id:node for node in (
                folder.folders + folder.files)}
            disk_node_ids = set(disk_nodes.keys())
            deleted_docs = es_node_ids - disk_node_ids
            new_docs = disk_node_ids - es_node_ids
            for doc_to_delete in deleted_docs:
                self.delete_document_by_id(doc_to_delete)
            for new_document in new_docs:
                self.index_document_by_node(disk_nodes[new_document])
            self.flush_index()
        else:
            app.logger.error('No folder found by passing node id: {node_id}'.format(
                node_id=node_id
            ))
            
    def do_full_sync(self):
        '''
        Do a full sync of the user filesystem. Find all folders from the
        user's filesystem compare them one by one. Then fetch all folders in
        ES and compare them for a cleanup. In case some folders have been 
        renamed.
        '''
        self.disable_realtime_indexing()
        disk_folders = Folder.find_all_folders(self.user)
        es_data = {"docs":[]}
        for folder in disk_folders:
            es_data["docs"].append({
                "_index" : self.user.uid,
                "_type" : "node",
                "_id" : folder.index_id,
                "fields" : ["_id"]
            })
        results = self.es_service.conn.get('_mget', data=es_data)
        if results['status'] == 200:
            es_results = [ d_id['_id'] for d_id in results['docs']
                           if d_id['exists'] == True ]
            for folder in disk_folders:
                if folder.index_id in es_results:
                    app.logger.debug(u'Syncing folder: {f}'.format(
                        f=folder.sys_path))
                    self.do_folder_sync(folder.index_id)
                else:
                    app.logger.debug(u'Created folder: {f}'.format(
                        f=folder.sys_path))
                    self.index_folders_and_files(folder=folder)
        else:
            app.logger.error(u'Couldn\'t fetch documents. Full sync stopped.')
            return
        max_size = int(self.es_service.conn.get(self.count_url, data={
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "type": Node.FOLDER_TYPE
                        }
                    }]
                }
            }
        })['hits']['total'])
        search_url = '{idx_name}/_search'.format(idx_name=self.user.uid)
        es_docs = self.es_service.conn.get(search_url, data={
            "from": 0,
            "size": max_size,
            "fields": [],
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "type": Node.FOLDER_TYPE
                        }
                    }]
                }
            }
        })['hits']['hits']
        es_docs = {doc['_id']:doc for doc in es_docs}
        folder_nodes = {folder.index_id:folder for folder in disk_folders}
        es_folders = set(es_docs.keys())
        folders = set(folder_nodes.keys())
        deleted_docs = es_folders - folders
        deleted_ids = []
        for doc_to_delete in deleted_docs:
            deleted_ids += self.delete_document_by_parent_id(doc_to_delete)
            if doc_to_delete not in deleted_ids:
                deleted_ids.append(
                    self.delete_document_by_id(doc_to_delete))
        app.logger.debug(u'Deleted nodes with id like:\n {name}'
            .format(name=deleted_ids))
        self.enable_realtime_indexing()
        self.optimize_index()
        self.flush_index()
        
    def flush_index(self):
        '''
        The flush process of an index basically frees memory from the index by
        flushing data to the index storage and clearing the internal
        transaction log. By default, ElasticSearch uses memory heuristics in
        order to automatically trigger flush operations as required in order
        to clear memory.
        '''
        url = '{idx_name}/_flush'.format(idx_name=self.user.uid)
        self.es_service.conn.post(url, data={})
        
    def optimize_index(self):
        '''
        The optimize process basically optimizes the index for faster search 
        operations (and relates to the number of segments a lucene index holds
        within each shard).
        
        Should the optimize process only expunge segments with deletes in it. 
        In Lucene, a document is not deleted from a segment, just marked as
        deleted. During a merge process of segments, a new segment is created
        that does not have those deletes. This flag allow to only merge 
        segments that have deletes.
        '''
        url = '{idx_name}/_optimize?only_expunge_deletes=true'.format(idx_name=self.user.uid)
        self.es_service.conn.post(url, data={})
        
    def disable_realtime_indexing(self):
        ''' 
        Increase the refresh interval to disable realtime indexing
        '''
        self.es_service.conn.put(self.settings_url, data={
            "index": {
                "refresh_interval" : "120s"
            }
        })
    def enable_realtime_indexing(self):
        ''' 
        Decrease the refresh interval to enable realtime indexing
        '''
        self.es_service.conn.put(self.settings_url, data={
            "index": {
                "refresh_interval" : "1s"
            }
        })
    
    @staticmethod
    def index_all_users():
        ''' Static method for indexing all folders and files for all users '''
        users = User.get_users()
        for user in users:
            try:
                TaskService(build_process, user=user)
            except ValueError, error:
                app.logger.error(error)
        return len(users)
    
    @staticmethod
    def sync_all_users():
        ''' Static method for syncing all folders and files for all users '''
        users = User.get_users()
        for user in users:
            try:
                TaskService(full_sync_process, user=user)
            except ValueError, error:
                app.logger.error(error)
        return len(users)

def build_process(values):
    ''' Task/process function '''
    user = values.get('user')
    if user:
        service = UserDataService(user)
        service.build_index()
        app.logger.info('Index built for user: {uid}.'.format(uid=user.uid))
        
def full_sync_process(values):
    ''' Task/process function '''
    user = values.get('user')
    if user:
        service = UserDataService(user)
        service.do_full_sync()
        app.logger.info('Full sync for {uid} done.'.format(uid=user.uid))
        
def folder_sync_process(values):
    ''' Task/process function '''
    user = values.get('user')
    node_id = values.get('node_id')
    if user and node_id:
        service = UserDataService(user)
        service.do_folder_sync(node_id)
        app.logger.info('Folder sync for {uid} done.'.format(uid=user.uid))