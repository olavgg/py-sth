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

Created on Jan 2, 2013

@Author: Olav Groenaas Gjerde
"""
import warnings

from flask import Blueprint
from flask import jsonify
from flask import abort

from flask import current_app as app
from conf.security import with_http_auth
from conf.security import disallow_special_characters
from services.user_data_service import UserDataService
from services.es_service import EsService
from services.task_service import TaskService as TS
from services.user_data_service import build_process
from services.user_data_service import full_sync_process
from services.user_data_service import folder_sync_process
from domain.user import User

PAGE = Blueprint('es_page', __name__)
USER_ERROR_MSG = u"User {u} home folder doesn't exist."


@PAGE.route("/es", methods=['GET', 'POST'])
@with_http_auth
def index():
    """
    Show status
    """
    es_service = EsService()
    return jsonify(es_service.get_status())


@PAGE.route("/es/<uid>", methods=['GET', 'POST'])
@with_http_auth
def list_all(uid):
    """
    List data from the specified user
    """
    user = User.get(uid)
    data = UserDataService(user).find_all_folders()
    return jsonify(data)


@PAGE.route("/es/build/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def build(uid):
    """
    Build new index for the specified user, build folders first and then
    later fill it with files. This function is heavy, so it executes
    asynchronously.
    """
    user = User.get(uid)
    if user:
        try:
            TS(build_process, user=user)
        except ValueError, error:
            app.logger.error(error)
            return jsonify(dict(error='job is already running')), 200
        data = dict(status='job created')
        return jsonify(data), 201
    abort(404, USER_ERROR_MSG.format(u=uid))


@PAGE.route("/es/build/all/", methods=['GET', 'POST'])
@with_http_auth
def build_all():
    """
    Build new index for all users
    """
    total = UserDataService.index_all_users()

    data = dict(status='ok',
                jobs=total,
                description='{total} jobs created'.format(total=total))
    return jsonify(data), 200


@PAGE.route("/es/create/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def create(uid):
    """
    Create new index for the specified user.
    :param uid:
    """
    warnings.warn(("This function shouldn't be used, instead this application "
                   "should automatically find the new filesystem and create "
                   "the index for it."), DeprecationWarning)
    user = User.get(uid)
    if user:
        return jsonify(EsService().create_index(user.uid, overwrite=True))
    abort(404, USER_ERROR_MSG.format(u=uid))


@PAGE.route("/es/destroy/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def destroy_idx(uid):
    """
    Destroy index for the specified user.
    """
    warnings.warn(("This function shouldn't be used, instead this application "
                   "should automatically find the deleted filesystem and "
                   "destroy its index."), DeprecationWarning)
    user = User.get(uid)
    if user:
        return jsonify(EsService().destroy_index(user.uid))
    abort(404, USER_ERROR_MSG.format(u=uid))


@PAGE.route("/es/sync/all/", methods=['GET', 'POST'])
@with_http_auth
def sync_all():
    """
    Sync the filesystem and ES DB by scanning and comparing datastructures
    on both the filesystem and ES DB.
    """
    total = UserDataService.sync_all_users()
    data = dict(status='ok',
                jobs=total,
                description='{total} jobs created'.format(total=total))
    return jsonify(data), 200


@PAGE.route("/es/sync/<string:uid>/", methods=['GET', 'POST'])
@with_http_auth
def sync_uid(uid):
    """
    Sync the filesystem and ES DB by scanning and comparing datastructures
    on both the filesystem and ES DB.
    """
    user = User.get(uid)
    if user:
        try:
            TS(full_sync_process, user=user)
        except ValueError, error:
            app.logger.error(error)
            return jsonify(dict(error='job is already running')), 200
        data = dict(status='job created')
        return jsonify(data), 201
    abort(404, USER_ERROR_MSG.format(u=uid))


@PAGE.route("/es/sync/<string:uid>/<string:node_id>", methods=['GET', 'POST'])
@with_http_auth
def sync_folder(uid, node_id):
    """
    Sync the folder by comparing datastructures on both the filesystem and the
    ES DB.
    """
    user = User.get(uid)
    if user:
        try:
            TS(folder_sync_process, user=user, node_id=node_id)
        except ValueError, error:
            app.logger.error(error)
            return jsonify(dict(error='job is already running')), 200
        data = dict(status='job created')
        return jsonify(data), 201
    abort(404, USER_ERROR_MSG.format(u=uid))