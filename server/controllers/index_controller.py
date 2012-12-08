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
from flask import request

from conf.base import Base

PAGE = Blueprint('index_page', __name__)

@PAGE.route("/", methods=['GET', 'POST'])
def index():
    '''
    Render application index page
    '''
    data = dict(
        title = "Python Storage Tank Helper",
        online = True
    )
    return jsonify(data)

@PAGE.route("/testauth", methods=['GET', 'POST'])
def test_auth():
    '''
    test if authentication is working
    '''
    base = Base.get_instance()
    is_authed = False
    if request.args.get('password') == base.app.config["APPPW"]:
        is_authed = True
    data = dict(
        authed = str(is_authed)
    )
    return jsonify(data)

