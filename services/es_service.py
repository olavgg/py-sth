"""
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
"""

from external_projects import rawes
from requests import ConnectionError
import json

from flask import current_app as app


class EsService(object):
    """ Handles connecting to a ElasticSearch cluster and data manipulation """

    current_connection = None

    def __init__(self):
        """
        Hard coded connection for now. ElasticSearch supports load balancing
        with the option to set node.data to false. Read more on
        www.elasticsearch.org/guide/reference/modules/node.html
        """
        try:
            es_server = 'es01:9200'
            self.conn = rawes.Elastic(es_server)
            if self.conn is None:
                es_server = 'es02:9200'
                self.conn = rawes.Elastic(es_server)
                if self.conn is None:
                    # noinspection PyExceptionInherit
                    raise ConnectionError(
                        u"Couldn't connect to %s" % es_server)
        except ConnectionError as err:
            app.logger.exception(str(err))
        EsService.current_connection = self

    @staticmethod
    def get_instance():
        """
         Returns a new ElasticSearch connection instance
        """
        if EsService.current_connection is None:
            return EsService()
        return EsService.current_connection

    def get_status(self):
        """
        Get connection status to ES
        """
        return self.conn.get('')

    def create_index(self, name, data=None, overwrite=False):
        """
        Create index , overwrite if a third argument/overwrite with value true
        is passed. Index name is automatically lower cased.
        """
        if not data:
            data = dict()
        name = name.lower()
        if overwrite:
            idx_exists = self.conn.head(name)
            if idx_exists:
                self.conn.delete(name)
        result = self.conn.put(name, data=data)
        if result['status'] != 200:
            app.logger.error(u"Couldn't create index")
        return result

    def bulk_insert(self, path, data, bulk_size=8000):
        """
        Bulk insert data to ElasticSearch, default size of bulk_size is 8000
        """
        counter = 0
        data_buffer = []
        for item in data:
            if counter == bulk_size:
                self.__do_bulk_insert(path, data_buffer)
                counter = 0
                data_buffer = []
            data_buffer.append(item)
            counter += 1
        if data_buffer:
            self.__do_bulk_insert(path, data_buffer)

    def __do_bulk_insert(self, path, databulk):
        """
        Private function that does the actual bulk insert to ES
        """
        data_buffer = '\n'.join([json.dumps(bdat) for bdat in databulk]) + '\n'
        result = self.conn.post(path, data=data_buffer)
        if result['status'] != 200:
            app.logger.error(str(result))
            app.logger.error(data_buffer)
            app.logger.error(u"Couldn't do bulk insert")

    def destroy_index(self, name):
        """
        Destroy Index
        """
        name = name.lower()
        idx_exists = self.conn.head(name)
        if idx_exists:
            result = self.conn.delete(name)
            if result['status'] != 200:
                app.logger.error(u"Couldn't destroy ES index")
            else:
                app.logger.info(u"Index: '{idx}' DESTROYED.".format(idx=name))
            return result
        return dict(error=u'Index not found')