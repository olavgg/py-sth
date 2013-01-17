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

Created on Jan 2, 2013

@Author: Olav Groenaas Gjerde
'''

from flask import Blueprint
from flask import jsonify
from flask import abort

from conf import LOG
from conf.security import with_http_auth
from conf.security import disallow_special_characters
from services.user_data_service import UserDataService
from services.es_service import EsService
from services.task_service import TaskService as TS
from services.user_data_service import build_process
from domain.user import User

PAGE = Blueprint('es_page', __name__)

@PAGE.route("/es", methods=['GET', 'POST'])
@with_http_auth
def index():
    ''' Show status '''
    es_service = EsService()
    return jsonify(es_service.get_status())

@PAGE.route("/es/<uid>", methods=['GET', 'POST'])
@with_http_auth
def listall(uid):
    ''' List data from the specified user '''
    user = User.get(uid)
    data = UserDataService(user).find_all()
    return jsonify(data)

@PAGE.route("/es/build/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def build(uid):
    '''
    Build new index for the specified user, build folders first and then
    later fill it with files. This function is heavy, so it executes
    asynchronously.
    '''
    user = User.get(uid)
    if user:
        try:
            TS(build_process, user=user)
        except ValueError, error:
            LOG.error(error)
            return jsonify(dict(error='job is already running'))
        data = dict(status='ok')
        return jsonify(data)
    abort(404)
    
@PAGE.route("/es/build/all/", methods=['GET', 'POST'])
@with_http_auth
def build_all():
    ''' Build new index for all users '''
    total = UserDataService.index_all_users()
    
    data = dict(status='ok',
                jobs=total,
                description='{total} jobs created'.format(total=total))
    return jsonify(data)

@PAGE.route("/es/create/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def create(uid):
    ''' Create new index for the specified user'''
    user = User.get(uid)
    if user:
        return jsonify(EsService().create_index(user.uid, overwrite=True))
    abort(404)

@PAGE.route("/es/update/folder/<node_id>/<uid>/", methods=['GET','POST'])
@with_http_auth
def update_folder(node_id, uid):
    ''' Update folder '''
    data = {}
    return jsonify(data)

@PAGE.route("/es/update/index/<uid>/", methods=['GET','POST'])
@with_http_auth
def update_index(uid):
    ''' Update folder '''
    user = User.get(uid)
    if user:
        UserDataService(user).do_full_sync()
    
    data = {}
    return jsonify(data)

@PAGE.route("/es/get/<idx_id>/<user>/", methods=['GET','POST'])
@with_http_auth
def get_folder(idx_id, user):
    ''' Return folder contents '''
    data = {}
    return jsonify(data)