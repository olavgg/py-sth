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

DO NOT USE THIS!!!!
'''

import os
import logging
from Crypto.Util.number import getRandomInteger
from datetime import timedelta
from apscheduler.scheduler import Scheduler

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import jsonify

from conf.base import Base
from conf.boostrap import Bootstrap
from services.user_data_service import UserDataService

CONFIG_TYPE='ProductionConfig'
APP = Flask(__name__)
APP.config.from_object('conf.config.%s'%(CONFIG_TYPE))
APP.secret_key = getRandomInteger(128)
APP.permanent_session_lifetime = timedelta(seconds=10)
#Imports all controllers and register pages
CONTROLLERS = []
for controller in os.listdir(os.getcwd()+"/controllers"):
    module_name, ext = os.path.splitext(controller)
    if module_name.endswith('_controller') and ext == '.py':
        module = __import__("controllers.%s"%(module_name))
        CONTROLLERS.append(module.__getattribute__(module_name))
for controller in CONTROLLERS:
    APP.register_blueprint(controller.PAGE)
    
logging.basicConfig(
    filename=APP.config["LOGFILE"],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
)
sched = Scheduler()
@sched.interval_schedule(seconds=60)
def index_all_users_job():
    with APP.app_context():
        UserDataService.index_all_users()
sched.start()
    
@APP.errorhandler(400)
def bad_request(exception):
    '''Bad Request'''
    data = dict(
        status = exception.code, 
        error = str(exception),
        description = bad_request.__doc__
    )
    return jsonify(data), 400

@APP.errorhandler(404)
def page_not_found(exception):
    '''Page Not Found'''
    data = dict(
        status = exception.code, 
        error = str(exception),
        description = page_not_found.__doc__
    )
    return jsonify(data), 404

if APP.config['DEBUG'] == True:
    @APP.errorhandler(500)
    def error(exception):
        '''Internal Server Error'''
        data = dict(
            status = exception.code, 
            error = str(exception),
            description = error.__doc__
        )
        return jsonify(data), 500

@APP.errorhandler(403)
def forbidden(exception):
    '''Forbidden'''
    data = dict(
        status = exception.code, 
        error = str(exception),
        description = forbidden.__doc__
    )
    return jsonify(data), 403

@APP.before_first_request
def bootstrap():
    Bootstrap()
with APP.app_context():
    Base.do_first_request()
APP.wsgi_app = ProxyFix(APP.wsgi_app)

