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
from Crypto.Util.number import getRandomInteger
from datetime import timedelta
from flask import Flask
from flask import jsonify

class Base(object):
    '''
    Base application functionality
    '''
    _base = None

    def __init__(self, config_type='DevelopmentConfig'):
        app = Flask(__name__)
        self.app = app
        self.app.config.from_object('conf.config.%s'%(config_type))
        self.app.secret_key = getRandomInteger(128)
        self.app.permanent_session_lifetime = timedelta(seconds=10)
        Base._base = self
        
        @app.errorhandler(404)
        def page_not_found(exception):
            '''Page Not Found'''
            data = dict(
                status = exception.code, 
                error = str(exception),
                description = page_not_found.__doc__
            )
            return jsonify(data)
        
        if app.config['DEBUG'] == False:
            @app.errorhandler(500)
            def error(exception):
                '''Internal Server Error'''
                data = dict(
                    status = exception.code, 
                    error = str(exception),
                    description = error.__doc__
                )
                return jsonify(data)
        
        @app.errorhandler(403)
        def forbidden(exception):
            '''Forbidden'''
            data = dict(
                status = exception.code, 
                error = str(exception),
                description = forbidden.__doc__
            )
            return jsonify(data)
        
    @staticmethod
    def get_instance():
        '''
        Get current static Base instance, create a new if it doesn't exist
        '''
        if Base._base == None:
            Base._base = Base()
        return Base._base
    
    @staticmethod
    def get_new_instance():
        '''
        Get a new Base instance
        '''
        Base._base = Base()
        return Base._base
    