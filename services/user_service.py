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

Created on Feb 5, 2013

@Author: Olav Groenaas Gjerde
"""
import os
from flask import current_app as app

from domain.user import User
from services.user_data_service import UserDataService


class UserService(object):
    """ User service class"""

    @staticmethod
    def find_users_in_home_path():
        """ Create a new user for every user in home path """
        path = app.config['USER_HOME_PATH']
        users = [o for o in os.listdir(path) if (
            os.path.isdir(path + '/' + o) and not
            os.path.islink(path + '/' + o))]
        for user in users:
            User(user)

    @staticmethod
    def sync_users():
        """
        Create a new index if a new filesystem is found and sync it.
        Delete the index if the filesystem has been removed.
        """
        home_path = app.config['USER_HOME_PATH']
        temp_path = app.config['USER_TEMP_PATH']
        users = [(o, False) for o in os.listdir(home_path) if (
            os.path.isdir(home_path + '/' + o) and not
            os.path.islink(home_path + '/' + o))]
        users += [(o, True) for o in os.listdir(temp_path) if (
            os.path.isdir(temp_path + '/' + o) and not
            os.path.islink(temp_path + '/' + o))]
        new_users = set(users) - set(User.users.keys())
        deleted_users = set(User.users.keys()) - set(users)
        for user in new_users:
            user_obj = User(user[0], anonymous=user[1])
            service = UserDataService(user_obj)
            service.build_index()
            app.logger.info(u"Added user: {u}. Is anonymous: {isAno}"
                            .format(u=user[0], isAno=user[1]))
        for user in deleted_users:
            service = UserDataService(User.get(user[0]))
            service.destroy_index()
            del User.users[user[0]]
            app.logger.info(u"Deleted user: {u}.".format(u=user[0]))