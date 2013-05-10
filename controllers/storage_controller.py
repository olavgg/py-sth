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

Created on May 1, 2013

@Author: Olav Groenaas Gjerde
"""

from flask import Blueprint
from flask import jsonify, abort

from conf.security import with_http_auth, disallow_special_characters
from domain.user import User
from services.zfs_service import ZFSService

PAGE = Blueprint('storage_page', __name__)

USER_ERROR_MSG = u"User {u} home folder doesn't exist."


@PAGE.route("/zfs/create/anonymous/<string:uid>/<int:size>",
            methods=['GET', 'POST'])
@with_http_auth
@disallow_special_characters
def create_anonymous(uid, size):
    """
    Create ZFS Filesystem for user
    :param uid:
    :param size:
    """
    zfs_service = ZFSService(uid)
    data = zfs_service.create(size)
    if data is not True:
        abort(500, data['error'])
    return jsonify(data)


@PAGE.route("/zfs/create/<string:uid>/<int:size>", methods=['GET', 'POST'])
@with_http_auth
@disallow_special_characters
def create(uid, size):
    """
    Create ZFS Filesystem for user
    :param uid:
    :param size:
    """
    zfs_service = ZFSService(uid)
    data = zfs_service.create(size)
    if data is not True:
        abort(500, data['error'])
    return jsonify(data)


def destroy(uid):
    user = User.get(uid)
    if user:
        zfs_service = ZFSService(uid)
        data = zfs_service.destroy(user)
        if data is not True:
            abort(500, data['error'])
        return jsonify(data)
    abort(404, USER_ERROR_MSG.format(u=uid))