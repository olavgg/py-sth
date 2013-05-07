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

Created on May 4, 2013

@Author: Olav Groenaas Gjerde
"""
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from flask import current_app as app
from domain.user import User
from services.user_data_service import UserDataService


class FSWatcher(object):
    def __init__(self):
        """
        Watch two folders
        """
        event_handler = BackupBayFSEventHandler()
        observer1 = Observer()
        folder = app.config['USER_HOME_PATH']
        observer1.schedule(event_handler, folder, recursive=False)
        app.logger.info(u"Watching folder: {f}".format(f=folder))
        observer2 = Observer()
        folder = app.config['USER_TEMP_PATH']
        observer2.schedule(event_handler, folder, recursive=False)
        app.logger.info(u"Watching folder: {f}".format(f=folder))
        observer1.start()
        observer2.start()


class BackupBayFSEventHandler(FileSystemEventHandler):
    """
    Handles all the events captured.
    """
    def __init__(self):
        """
        Constructor
        :return:
        """
        FileSystemEventHandler.__init__(self)
        self.app = app._get_current_object()

    def on_created(self, event):
        """
        When something is created in a watched folder, this event executes.
        :param event:
        :return:
        """
        super(BackupBayFSEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        self.app.logger.info("Created %s: %s", what, event.src_path)
        self.__handle_created_event(event.src_path)

    def on_deleted(self, event):
        """
        When something is deleted in a watched folder, this event executes.
        :param event:
        :return:
        """
        super(BackupBayFSEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        self.app.logger.info("Deleted %s: %s", what, event.src_path)
        self.__handle_deleted_event(event.src_path)

    def __handle_created_event(self, folder):
        """
        Creates an index by finding the name of the new filesystem
        :param folder:
        :return:
        """
        username, isAnonymous = self.__handle_event(folder)
        with self.app.app_context():
            user = User(username, anonymous=isAnonymous)
            user_service = UserDataService(user)
            user_service.build_index()

    def __handle_deleted_event(self, folder):
        """
        Destroys the index by finding the name of the deleted filesystem
        :param folder:
        :return:
        """
        username, isAnonymous = self.__handle_event(folder)
        with self.app.app_context():
            user = User.get(username)
            user_service = UserDataService(user)
            user_service.destroy_index()
            del User.users[username]

    def __handle_event(self, folder):
        """
        Find and return the name of the new filesystem, based on path the
        event occurred we
        :param folder:
        :return tuple(str, boolean):
        """
        home_folder = self.app.config['USER_HOME_PATH']
        temp_folder = self.app.config['USER_TEMP_PATH']
        username = u''
        isAnonymous = False
        if folder.find(temp_folder) == 0:
            username = folder[len(temp_folder)+1:]
            isAnonymous = True
        elif folder.find(home_folder) == 0:
            username = folder[len(home_folder)+1:]
        return username, isAnonymous
