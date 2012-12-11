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

Created on Dec 11, 2012

@Author: Olav Groenaas Gjerde
'''
from functools import wraps
from flask import request
from conf.base import Base

def with_http_auth(func):
    '''Decorator'''
    @wraps(func)
    def validate_token(*args, **kwargs):
        '''
        Check if the token exists in http headers or within the post or get
        http methods. Validate them
        '''
        base = Base.get_instance()
        auth_token = base.app.config["AUTH_TOKEN"]
        # Check HTTP Header
        if (request.headers.has_key("Authtoken") == True and
            request.headers.get("Authtoken") == auth_token):
            return func(*args, **kwargs)
        # Check GET/POST param
        #elif (base.app.config["DEBUG"] == True and 
        #      request.args.has_key('password') and
        #    request.args.get('password') == auth_token
        #    ) or ( base.app.config["DEBUG"] == True and
        #    request.form.has_key('password') and
        #    request.form.get('password') == auth_token):
        #    return func(*args, **kwargs)
        else:
            return "no access"
    return validate_token