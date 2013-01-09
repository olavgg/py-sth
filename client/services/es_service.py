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

from conf import LOG

class EsService(object):
    ''' Handles connecting to a ElasticSearch cluster and data manipulation '''
    
    current_connection = None

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
        EsService.current_connection = self
        
    @staticmethod
    def get_instance():
        if EsService.current_connection == None:
            return EsService()
        return EsService.current_connection
            
    def get_status(self):
        return self.conn.get('')
            
    def create_index(self, name, data=dict(), overwrite=False):
        ''' 
        Create index , overwrite if a third argument/overwrite with value true
        is passed. 
        '''
        if overwrite:
            idx_exists = self.conn.head(name)
            if idx_exists:
                self.conn.delete(name)
        result = self.conn.put(name, data=data)
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
            