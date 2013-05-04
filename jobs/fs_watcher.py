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
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from flask import current_app as app
from services.task_service import TaskService


class FSWatcher(object):
    def __init__(self):
        """
        Creates a start the filesystem watch process
        """
        try:
            TaskService(start_watchdog, parentID=os.getppid(), user='home')
            TaskService(start_watchdog, parentID=os.getppid(), user='temp')
        except ValueError, error:
            app.logger.error(error)


def start_watchdog(values):
    """
    Start the watchdog process
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = FSEventHandler()
    observer = Observer()
    if values.get('user') == 'home':
        observer.schedule(
            event_handler, app.config['USER_HOME_PATH'], recursive=False)
    elif values.get('user') == 'temp':
        observer.schedule(
            event_handler, app.config['USER_TEMP_PATH'], recursive=False)
    observer.start()
    if os.getppid() != values.get('parentID'):
        time.sleep(1)
    observer.stop()
    observer.join()


class FSEventHandler(FileSystemEventHandler):
    """
    Handles all the events captured.
    """

    def on_moved(self, event):
        super(FSEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        app.logger.info("Moved %s: from %s to %s", what, event.src_path,
                        event.dest_path)

    def on_created(self, event):
        super(FSEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        app.logger.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(FSEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        app.logger.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(FSEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        app.logger.info("Modified %s: %s", what, event.src_path)
