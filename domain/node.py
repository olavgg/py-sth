"""
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

Created on Jan 18, 2013

@Author: Olav Groenaas Gjerde
"""

import os
import errno
from urllib import unquote_plus
from urllib import quote_plus
import datetime
from flask import current_app as app


class Node(object):
    """ Simple representation of a file/folder object """

    FILE_TYPE = u'FILE'
    FOLDER_TYPE = u'FOLDER'

    def __init__(self, values):
        """ Constructor, added fix for quote_plus lack of unicode support """
        self.__name = values['name']
        values['path'] = values['path'].encode('utf-8')
        self.__index_id = unicode(quote_plus(values['path']))
        self.__path = values['path']
        self.__sys_path = values['sys_path']
        self.__date_modified = values['date_modified']
        self.__type = values['type']

    @staticmethod
    def get_instance(path, decode=False, node_type=None):
        """ Create node meta-data by reading it from disk """
        if decode:
            path = unquote_plus(path)
        disk_path = app.config['USER_HOME_PATH'] + path
        if os.path.exists(disk_path):
            if os.path.isfile(disk_path):
                node_type = Node.FILE_TYPE
            elif os.path.isdir(disk_path):
                node_type = Node.FOLDER_TYPE
            date_modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(disk_path)).strftime(app.config['DATEFORMAT'])
            values = {
                'name': os.path.basename(disk_path),
                'path': path,
                'sys_path': disk_path,
                'date_modified': date_modified,
                'type': node_type
            }
        else:
            error_msg = u"path doesn't exist: {path}".format(path=disk_path)
            app.logger.error(error_msg)
            raise ValueError(error_msg)
        return Node(values)

    @property
    def index_id(self):
        """ Get id """
        return self.__index_id

    @index_id.setter
    def index_id(self, value):
        """ Set name """
        value = value.encode('utf-8')
        self.__index_id = quote_plus(value)

    @property
    def path(self):
        """ Get path """
        if not isinstance(self.__path, unicode):
            return unicode(self.__path, 'utf-8')
        return self.__path

    @path.setter
    def path(self, value):
        """ Set path """
        self.__path = value

    @property
    def sys_path(self):
        """ Get full system path """
        return self.__sys_path

    @sys_path.setter
    def sys_path(self, value):
        """ Set full system path """
        self.__sys_path = value

    @property
    def name(self):
        """ Get name """
        return self.__name

    @name.setter
    def name(self, value):
        """ Set name """
        self.__name = value

    @property
    def date_modified(self):
        """ Get date modified """
        return self.__date_modified

    @date_modified.setter
    def date_modified(self, value):
        """ Set date modified """
        self.__date_modified = value

    @property
    def type(self):
        """ Get type """
        return self.__type

    @type.setter
    def type(self, value):
        """ Set type """
        self.__type = value

    def get_parent(self):
        """ Return parent folder for node """
        return self.path[:-(len(self.name) + 1)]

    def get_size(self):
        """ Return node disk size """
        return Node.sizeof_fmt(os.path.getsize(unicode(self.sys_path)))

    @staticmethod
    def sizeof_fmt(num):
        """ Byte representation"""
        for x in [' bytes', ' KB', ' MB', ' GB']:
            if 1024.0 > num > -1024.0:
                if x == ' bytes':
                    return "%3i%s" % (num, x)
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    @staticmethod
    def is_broken_symlink(path):
        """ Check if symlink is broken """
        if os.path.islink(path):
            try:
                os.stat(path)
            except os.error, err:
                if err.errno == errno.ENOENT:
                    app.logger.error('broken link')
                elif err.errno == errno.ELOOP:
                    app.logger.error('circular link')
                app.logger.error(err)
                return True
        return False