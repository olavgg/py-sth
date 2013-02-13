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

from flask import current_app as app

from domain.node import Node
from services.shell_command import ShellCommand

class Folder(Node):
    ''' Folder class '''

    def __init__(self, values):
        ''' Constructor '''
        Node.__init__(self, values)
        self.__parent = Node.get_instance(self.get_parent())
        self.__files = []
        self.__folders = []
        
    @staticmethod
    def get_instance(path, decode=False):
        ''' Create folder meta-data by reading it from disk '''
        if decode:
            path = unicode(unquote_plus(path.encode('utf-8')),'utf-8')
        disk_path = app.config['USER_HOME_PATH'] + path
        if os.path.exists(disk_path) == True:
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(app.config['DATEFORMAT'])
            values = {
                'name':os.path.basename(disk_path),
                'path':path,
                'sys_path':disk_path,
                'date_modified':date_modified,
                'type':'FOLDER'
            }
        else:
            error_msg = u"path doesn't exist: {path}".format(path=disk_path)
            app.logger.error(error_msg)
            raise ValueError(error_msg)
        return Folder(values)
    
    @property
    def parent(self):
        ''' Get parent '''
        return self.__parent
    
    @property
    def files(self):
        ''' Get files '''
        if not self.__files:
            self.scan_for_files()
        return self.__files
    
    def scan_for_files(self):
        ''' Scan for files '''
        try:
            files = [o for o in os.listdir(
                self.sys_path) if (os.path.isfile(self.sys_path+'/'+o) and not
                os.path.islink(self.sys_path+'/'+o))]
        except UnicodeEncodeError, e:
            app.logger.error(str(e))
            app.logger.error(type(self.sys_path))
            app.logger.error(self.sys_path)
            new_path = self.sys_path.encode('utf-8')
            files = [o for o in os.listdir(
                new_path) if (os.path.isfile(new_path+'/'+o) and not
                os.path.islink(new_path+'/'+o))]
        except UnicodeDecodeError, e:
            app.logger.error(str(e))
            app.logger.error(type(self.sys_path))
            app.logger.error(self.sys_path)
            new_path = self.sys_path.decode('utf-8')
            files = [o for o in os.listdir(
                new_path) if (os.path.isfile(new_path+'/'+o) and not
                os.path.islink(new_path+'/'+o))]
        for line in files:
            path = u'{folder}/{file}'.format(folder=self.path, file=line)
            node = Node.get_instance(path)
            self.__files.append(node)
    
    @files.setter
    def files(self, value):
        ''' Set files, new list if value is list or append a new File '''
        if isinstance(value, list):
            self.__files = value
        elif isinstance(value, Node):
            self.__files.append(value)
        else:
            raise TypeError('argument must be of type Node or List')
        
    @property
    def folders(self):
        ''' Get folders '''
        if not self.__folders:
            self.scan_for_folders()
        return self.__folders
    
    def scan_for_folders(self):
        ''' Scan for folders '''
        sub_folders = [o for o in os.listdir(
            self.sys_path) if (os.path.isdir(self.sys_path+'/'+o) and not
            os.path.islink(self.sys_path+'/'+o))]
        for line in sub_folders:
            path = u'{folder}/{node}'.format(folder=self.path, node=line)
            node = Node.get_instance(path)
            self.__folders.append(node)
    
    @folders.setter
    def folders(self, value):
        ''' Set folders, new list if value is list or append a new Folder. '''
        if isinstance(value, list):
            self.__folders = value
        elif isinstance(value, Node):
            self.__folders.append(value)
        else:
            raise TypeError('argument must be of type Node or List')
    
    @staticmethod
    def find_all_folders(user, folder=None):
        ''' Find all folders for user '''
        if folder == None:
            cmd = (u'find "{path}/{uid}" -type d | sed "s/\{path}//"').format(
                path = app.config['USER_HOME_PATH'],
                uid = user.uid,
            )
        else:
            cmd = (u'find "{path}" -type d | sed "s/\{path}//"').format(
                path = folder.syspath
            )
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            line = unicode(line, 'utf8')
            folders.append(Folder.get_instance(line))
        return folders