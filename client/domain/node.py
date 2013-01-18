'''
Created on Jan 18, 2013

@author: olav
'''

import os
from urllib import unquote_plus
from urllib import quote_plus
import datetime

from conf import CONFIG
from conf import LOG
from conf import DATEFORMAT

class Node(object):
    ''' Simple representation of a file/folder object '''
    
    def __init__(self, values):
        ''' Constructor '''
        self.__name = values['name']
        self.__index_id = values['name']
        self.__path = values['path']
        self.__sys_path = values['sys_path']
        self.__date_modified = values['date_modified']
        
    @staticmethod
    def get_instance(path, decode=False):
        ''' Create node meta-data by reading it from disk '''
        if decode:
            path = CONFIG['USER_HOME_PATH'] + unquote_plus(path)
        disk_path = CONFIG['USER_HOME_PATH'] + path
        if os.path.exists(disk_path):
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(DATEFORMAT)
            values = {
                'name':os.path.basename(disk_path),
                'path':path,
                'sys_path':disk_path,
                'date_modified':date_modified
            }
        else:
            error_msg = u"path doesn't exist"
            LOG.error(error_msg)
            raise ValueError(error_msg)
        return Node(values)
        
    @property
    def index_id(self):
        ''' Get id '''
        return self.__index_id
    
    @index_id.setter
    def index_id(self, value):
        ''' Set name '''
        self.__index_id = quote_plus(value)
        
    @property
    def path(self):
        ''' Get path '''
        return self.__path
    
    @path.setter
    def path(self, value):
        ''' Set path '''
        self.__path = value
        
    @property
    def sys_path(self):
        ''' Get full system path '''
        return self.__sys_path
    
    @sys_path.setter
    def sys_path(self, value):
        ''' Set full system path '''
        self.__sys_path = value
    
    @property
    def name(self):
        ''' Get name '''
        return self.__name
    
    @name.setter
    def name(self, value):
        ''' Set name '''
        self.__name = value
        
    @staticmethod
    def sizeof_fmt(num):
        ''' Byte representation'''
        for x in [' bytes','KB','MB','GB']:
            if num < 1024.0 and num > -1024.0:
                if x == ' bytes':
                    return "%3i%s" % (num, x)
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')