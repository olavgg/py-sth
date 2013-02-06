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

Created on Dec 8, 2012

@Author: Olav Groenaas Gjerde
'''

from flask import current_app as app

from services.task_service import TaskService

class Base(object):
    '''
    Base application functionality
    '''
    
    @staticmethod
    def do_first_request():
        '''
        Flask will run the initialization procedure two times, so this function
        is a workaround for the Flask framework limitation of initializing data
        at the application startup with the reloader enabled.
        '''
        try:
            TaskService(first_request_process, wait=True, sleep=1)
        except ValueError, err:
            app.logger.error(err)

def first_request_process(values):
    ''' First request Process to initialize data '''
    import urllib
    import time
    while True:
        time.sleep(values['sleep'])
        try:
            url = 'http://{url}:{port}'.format(
                url=app.config['HOST'],
                port=app.config['PORT'])
            res = urllib.urlopen(url)
            if res.getcode() == 200:
                break
        except IOError, err:
            app.logger.error(url)
            app.logger.error(err)