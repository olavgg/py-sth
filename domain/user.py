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

Created on Dec 11, 2012

@Author: Olav Groenaas Gjerde
"""
from flask import current_app as app

class User(object):
    """User object"""
    users = {}

    def __init__(self, uid, mock=False, anonymous=False):
        """Constructor"""
        self._uid = uid
        if anonymous is True:
            self._path = app.config['USER_HOME_PATH']
        else:
            self._path = app.config['USER_TEMP_PATH']
        if mock == False:
            User.users[uid] = self
            app.logger.info(u'Added user: ' + uid)

    def __str__(self):
        return self._uid
    
    @staticmethod
    def get_users_as_dict():
        """ Return all users as dictionary """
        return dict(users=User.get_users())
    
    @staticmethod
    def get_users():
        """ Return all users as list """
        return User.users.values()
    
    @staticmethod
    def get(uid):
        """ Find user by uid, return None if not found """
        if uid in User.users:
            return  User.users[uid]
        return None
        
    @property
    def uid(self):
        """ Get uid """
        return self._uid
    
    @uid.setter
    def uid(self, value):
        """ Set uid """
        self._uid = value