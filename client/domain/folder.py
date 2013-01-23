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
from services.shell_command import ShellCommand

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
            path = unquote_plus(path)
        disk_path = unicode(CONFIG['USER_HOME_PATH'] + path)
        if os.path.exists(disk_path) == True:
            parent_path = os.path.dirname(disk_path).replace(
                CONFIG['USER_HOME_PATH'], '')
            parent = Node.get_instance(parent_path)
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(DATEFORMAT)
            values = {
                'name':os.path.basename(disk_path),
                'path':path,
                'sys_path':disk_path,
                'parent':parent,
                'date_modified':date_modified,
                'type':'FOLDER'
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
        if not self.__files:
            self.scan_for_files()
        return self.__files
    
    def scan_for_files(self):
        ''' Scan for files '''
        files = [o for o in os.listdir(
            self.sys_path) if os.path.isfile(self.sys_path+'/'+o)]
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
            self.sys_path) if os.path.isdir(self.sys_path+'/'+o)]
        for line in sub_folders:
            path = '{folder}/{node}'.format(folder=self.path, node=line)
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
    def find_all_folders(user):
        ''' Find all folders for user '''
        cmd = ('find {path}/{uid} -type d | sed "s/\{path}//"').format(
            path = CONFIG['USER_HOME_PATH'],
            uid = user.uid,
        )
        results = ShellCommand(cmd).run()
        folders = []
        for line in results[0]:
            folders.append(Folder.get_instance(line))
        return folders