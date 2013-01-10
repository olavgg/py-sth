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
from domain.file import File

class Folder(object):
    ''' Folder class '''

    def __init__(self, values):
        ''' Constructor '''
        self.__files = []
        self.__folders = []
        self.__name = values['name']
        self.__index_id = None
        self.index_id(values['name'])
        self.__path = values['path']
        
        
    @staticmethod
    def get_instance(index_id, device_type):
        ''' Loads a file from type, DISK or ELASTICSEARCH '''
        values = {}
        if device_type == 'DISK':
            pass
        elif device_type == 'ELASTICSEARCH':
            pass
        else:
            raise TypeError('device_type must be of type Folder or List')
        return Folder(values)
    
    @property
    def index_id(self):
        ''' Get id '''
        return self.__index_id
    
    @index_id.setter
    def index_id(self, value):
        ''' Set name '''
        self.__index_id = value
        
    @property
    def path(self):
        ''' Get path '''
        return self.__path
    
    @path.setter
    def path(self, value):
        ''' Set path '''
        self.__path = value
    
    @property
    def name(self):
        ''' Get name '''
        return self.__name
    
    @name.setter
    def name(self, value):
        ''' Set name '''
        self.__name = value
    
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
    
        