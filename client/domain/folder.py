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

    def __init__(self, name):
        ''' Constructor '''
        self._files = []
        self._name = name
        
    @staticmethod
    def get_instance(name):
        return Folder(name)
    
    @property
    def name(self):
        ''' Get name '''
        return self._name
    
    @name.setter
    def name(self, value):
        ''' Set name '''
        self._name = value
    
    @property
    def files(self):
        ''' Get files '''
        return self._files
    
    @files.setter
    def files(self, value):
        ''' Set files, new list if value is list or append a new File '''
        if isinstance(value, list):
            self._files = value
        elif isinstance(value, File):
            self._files.append(value)
        else:
            raise TypeError('argument must be of type File or List')
        