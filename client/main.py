#!/usr/bin/env python
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
import logging
import os

from conf.base import Base
from conf.boostrap import Bootstrap
        
class PYSTHClient(object):
    '''
    Main class for application startup
    '''
    controllers = []
    
    @staticmethod
    def init_controllers(base):
        '''
        Imports all controllers and register pages
        '''
        for controller in os.listdir(os.getcwd()+"/controllers"):
            module_name, ext = os.path.splitext(controller)
            if module_name.endswith('_controller') and ext == '.py':
                module = __import__("controllers.%s"%(module_name))
                PYSTHClient.controllers.append(
                   module.__getattribute__(module_name))
        for controller in PYSTHClient.controllers:
            base.app.register_blueprint(controller.PAGE)
                
    @staticmethod
    def start():
        '''
        Start the application
        '''
        base = Base.get_instance()
        logging.basicConfig(
            filename=base.app.config["LOGFILE"],
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s '
                    '[in %(pathname)s:%(lineno)d]'
        )
        PYSTHClient.init_controllers(base)
        @base.app.before_first_request
        def bootstrap():
            Bootstrap()
        Base.do_first_request()
        base.app.run(base.app.config["HOST"], base.app.config["PORT"])
    
if __name__ == '__main__':
    PYSTHClient.start()