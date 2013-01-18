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

Created on Dec 23, 2012

@Author: Olav Groenaas Gjerde
'''
import os
from urllib import unquote_plus
import datetime

from conf import LOG
from conf import CONFIG
from conf import DATEFORMAT
from domain.file import File
from domain.node import Node

class Folder(Node):
    ''' Folder class '''

    def __init__(self, values):
        ''' Constructor '''
        Node.__init__(self, values)
        if isinstance(values['parent'], Node):
            self.__parent = values['parent']
        else:
            self.__parent = None
        self.__files = []
        self.__folders = []
        
    @staticmethod
    def get_instance(path, decode=False):
        ''' Create folder meta-data by reading it from disk '''
        if decode:
            path = CONFIG['USER_HOME_PATH'] + unquote_plus(path)
        disk_path = CONFIG['USER_HOME_PATH'] + path
        if os.path.exists(disk_path):
            parent = Node.get_instance(os.path.dirname(disk_path))
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(DATEFORMAT)
            values = {
                'name':os.path.basename(disk_path),
                'path':path,
                'sys_path':disk_path,
                'parent':parent,
                'date_modified':date_modified
            }
        else:
            error_msg = u"path doesn't exist"
            LOG.error(error_msg)
            raise ValueError(error_msg)
        return Folder(values)
    
    @property
    def parent(self):
        ''' Get parent '''
        return self.__parent
    
    @property
    def files(self):
        ''' Get files '''
        return self.__files
    
    @files.setter
    def files(self, value):
        ''' Set files, new list if value is list or append a new File '''
        if isinstance(value, list):
            self.__files = value
        elif isinstance(value, File):
            self.__files.append(value)
        else:
            raise TypeError('argument must be of type File or List')
        
    @property
    def folders(self):
        ''' Get folders '''
        return self.__folders
    
    @folders.setter
    def folders(self, value):
        ''' Set files, new list if value is list or append a new File '''
        if isinstance(value, list):
            self.__folders = value
        elif isinstance(value, Folder):
            self.__folders.append(value)
        else:
            raise TypeError('argument must be of type Folder or List')
    
        