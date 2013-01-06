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
from services.shell_command import ShellCommand

from conf.base import Base

class FolderService(object):
    ''' Load folders '''

    def __init__(self, user):
        '''Constructor'''
        from domain.user import User
        if isinstance(user, User) and isinstance(user.uid, str):
            base = Base.get_instance()
            self._path = "{path}/{uid}".format(
                path=base.app.config['USER_HOME_PATH'],
                uid=user.uid
            )
        else:
            raise TypeError('argument must be of type User')
    
    @property
    def path(self):
        ''' Get path '''
        return self._path
    
    @path.setter
    def path(self, value):
        ''' Set path '''
        self._path = value
    
    def find_all(self):
        ''' Find all folders for user '''
        cmd = 'ls -Ra {path} | grep -e "./.*:" | sed "s/://"'.format(
            path = self.path
        )
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            splitted_path = line.split('/')
            folder = splitted_path[len(splitted_path)-1]
            parent_folder = splitted_path[len(splitted_path)-2]
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(line)).strftime('%Y-%m-%d %H:%M')
            data = {'name':folder,'parent':parent_folder,
                'path':line,'date_modified':date_modified}
            folders.append(data)
        return dict(folders=folders)
        
    @staticmethod
    def sizeof_fmt(num):
        for x in [' bytes','KB','MB','GB']:
            if num < 1024.0 and num > -1024.0:
                if x == ' bytes':
                    return "%3i%s" % (num, x)
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')