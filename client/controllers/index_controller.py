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

from flask import Blueprint
from flask import jsonify
from flask import current_app

from conf.security import with_http_auth

from domain.user import User

PAGE = Blueprint('index_page', __name__)

@PAGE.route("/", methods=['GET', 'POST'])
def index():
    '''
    Render application index page
    '''
    print current_app.config['USER_HOME_PATH']
    data = dict(
        title = "Python Storage Tank Helper",
        online = True
    )
    return jsonify(data)

@PAGE.route("/testauth", methods=['GET', 'POST'])
@with_http_auth
def test_auth():
    '''
    test if authentication is working
    '''
    data = dict(authed = True)
    return jsonify(data)

@PAGE.route("/users", methods=['GET', 'POST'])
@with_http_auth
def users():
    ''' return all users that are registered '''
    return jsonify(User.get_users_as_dict())

