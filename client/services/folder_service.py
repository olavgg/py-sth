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
from conf import LOG

DATEFORMAT = '%Y-%m-%d %H:%M'

class FolderService(object):
    ''' Load folders '''
    
    def __init__(self, user):
        '''Constructor'''
        from domain.user import User
        if isinstance(user, User) and isinstance(user.uid, str):
            base = Base.get_instance()
            self.__syspath = base.app.config['USER_HOME_PATH']
            self.__path = "{path}/{uid}".format(
                path=self.__syspath,
                uid=user.uid
            )
        else:
            raise TypeError('argument must be of type User')
    
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
    
    def find_all(self):
        ''' Find all folders for user '''
        cmd = 'ls -Ra {path}/hg-projects | grep -e "./.*:"| sed "s/://;s/\/home//"'.format(
            path = self.path
        )
        LOG.debug(cmd)
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            splitted_path = line.split('/')
            folder = splitted_path[len(splitted_path)-1]
            parent_folder = line[:-len(folder)]
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(self.syspath+line)).strftime(DATEFORMAT)
            data = {'name':folder,'parent':parent_folder,
                'path':line,'date_modified':date_modified}
            folders.append(data)
        return folders
    
    def find_folder_files(self, folder):
        ''' Find all files for given folder '''
        cmd = 'find "{path}" -maxdepth 1 -type f | sed "s#.*/##"'.format(
            path = self.syspath + folder['path']
        )
        results = ShellCommand(cmd).run()
        files = []
        for line in results[0]:
            path = '{folder}/{file}'.format(folder=folder['path'],file=line)
            fullpath = self.syspath+path
            size = FolderService.sizeof_fmt(os.path.getsize(fullpath))
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(fullpath)).strftime(DATEFORMAT)
            data = {
                'name':line,'folder':folder['path'],'path':path,
                'size':size, 'date_modified':date_modified
            }
            files.append(data)
        return files
        
    @staticmethod
    def sizeof_fmt(num):
        for x in [' bytes','KB','MB','GB']:
            if num < 1024.0 and num > -1024.0:
                if x == ' bytes':
                    return "%3i%s" % (num, x)
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')