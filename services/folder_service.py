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

Created on Jan 9, 2013

@Author: Olav Groenaas Gjerde
'''
from domain.user import User

class FolderService(object):
    ''' Handles folder specific tasks for user '''
    def __init__(self, user):
        ''' Constructor '''
        if isinstance(user, User) and isinstance(user.uid, str):
            self.__user = user
            
    @property
    def user(self):
        ''' Get user '''
        return self.__user
            
    def create_folder(self):
        pass
    
    def rename_folder(self):
        pass
    
    def delete_folder(self):
        pass
    
    def copy_folder(self):
        pass
    
    def move_folder(self):
        pass
    
    def zip_folder(self):
        pass
        
    def gzip_folder(self):
        pass
        
    def lz4_folder(self):
        pass
        
    def xz_folder(self):
        pass