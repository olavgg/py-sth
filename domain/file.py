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

Created on Dec 23, 2012

@Author: Olav Groenaas Gjerde
"""
import os
import datetime
from urllib import unquote_plus

from flask import current_app as app

from domain.node import Node


class File(Node):
    """ File class """

    def __init__(self, values):
        """ Constructor """
        Node.__init__(self, values)
        self.__parent = Node.get_instance(self.get_parent())
        self.__size = values['size']
        
    @staticmethod
    def get_instance(path, decode=False, node_type=Node.FILE_TYPE, user=None):
        """ Create file meta-data by reading it from disk """
        if decode:
            path = unquote_plus(path)
        if user and user.isAnonymous():
            disk_path = app.config['USER_TEMP_PATH'] + path
        else:
            disk_path = app.config['USER_HOME_PATH'] + path
        app.logger.debug(disk_path)
        if os.path.exists(disk_path):
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(app.config['DATE_FORMAT'])
            values = {
                'name': os.path.basename(disk_path),
                'path': path,
                'sys_path': disk_path,
                'date_modified': date_modified,
                'type':Node.FILE_TYPE
            }
        else:
            error_msg = u"path doesn't exist: {path}".format(path=disk_path)
            app.logger.error(error_msg)
            raise ValueError(error_msg)
        return File(values)
    
    @property
    def size(self):
        """ Get size """
        return self.__size
    
    @size.setter
    def size(self, value):
        """ Set size """
        if isinstance(value,int) or isinstance(value,long):
            self.__size = Node.sizeof_fmt(value)
        else:
            self.__size = value
    
    @property
    def parent(self):
        """ Get parent """
        return self.__parent
    
    @parent.setter
    def parent(self, value):
        """ Set folder / parent that the file belongs to """
        if isinstance(value, Node):
            self.__parent = value
        else:
            raise TypeError(u'Argument must be of type Node')
        