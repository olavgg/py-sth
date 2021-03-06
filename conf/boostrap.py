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

Created on Dec 23, 2012

@Author: Olav Groenaas Gjerde
"""
from jobs.fs_watcher import FSWatcher

from services.user_service import UserService
from flask import current_app as app


class Bootstrap(object):
    """
    Bootstrap class, use this file to configure and setup data 
    that's needed for each environment.
    """

    def __init__(self):
        """
        Constructor, based on the environment settings,
        run the method for data initialization.
        """
        app.logger.info('Bootstrap starting...')
        if app.config['DEBUG'] is True:
            Bootstrap.init_dev_data()
        elif app.config['TESTING'] is True:
            Bootstrap.init_test_data()
        else:
            Bootstrap.init_prod_data()
        app.logger.info('Bootstrap complete...')

    @staticmethod
    def init_dev_data():
        """ Init dev data """
        UserService.sync_users()
        FSWatcher()
        #UserService.find_users_in_home_path()

    @staticmethod
    def init_test_data():
        """ Init test data """
        UserService.sync_users()

    @staticmethod
    def init_prod_data():
        """ Init prod data """
        UserService.sync_users()
        FSWatcher()
        #UserDataService.index_all_users()