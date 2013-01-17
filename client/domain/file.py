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

class File(object):
    ''' File class '''

    def __init__(self, name, folder):
        ''' Constructor '''
        from domain.folder import Folder
        if isinstance(folder, Folder):
            self._folder = folder
        else:
            self._folder = None
        self._name = name
        
    @staticmethod
    def get_instance(name, folder):
        return File(name, folder)
    
    @property
    def name(self):
        ''' Get name '''
        return self._name
    
    @name.setter
    def name(self, value):
        ''' Set name '''
        self._name = value
        
    @property
    def path(self):
        ''' Get path '''
        return self.__path
    
    @path.setter
    def path(self, value):
        ''' Set path '''
        self.__path = value
    
    @property
    def folder(self):
        ''' Get folder '''
        return self._folder
    
    @folder.setter
    def folder(self, value):
        ''' Set folder that the file belongs to '''
        if isinstance(value, Folder):
            self._folder = value
        else:
            raise TypeError('argument must be of type File or List')
        
    
        