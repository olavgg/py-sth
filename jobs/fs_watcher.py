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


class FSWatcher(object):
    def __init__(self):
        """
        Watch two folders
        """
        event_handler = FSEventHandler()
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


class FSEventHandler(FileSystemEventHandler):
    """
    Handles all the events captured.
    """
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.app = app._get_current_object()

    def on_moved(self, event):
        super(FSEventHandler, self).on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        self.app.logger.info ("Moved %s: from %s to %s", what, event.src_path,
               event.dest_path)

    def on_created(self, event):
        super(FSEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        self.app.logger.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(FSEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        app.logger.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(FSEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        self.app.logger.info("Modified %s: %s", what, event.src_path)
