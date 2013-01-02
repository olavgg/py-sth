'''
Created on Jan 2, 2013

@author: olav
'''

from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import url_for

from conf.security import with_http_auth
from services.folders import Folders
from domain.user import User

PAGE = Blueprint('es_page', __name__)

@PAGE.route("/es", methods=['GET', 'POST'])
@with_http_auth
def index():
    ''' Show status '''
    return redirect(url_for('.listall'))

@PAGE.route("/es/<uid>", methods=['GET', 'POST'])
@with_http_auth
def listall(uid):
    ''' List data from the specified user '''
    user = User.get(uid)
    data = Folders(user).find_all()
    return jsonify(data)

@PAGE.route("/es/create/<user>/", methods=['GET', 'POST'])
@with_http_auth
def create(user):
    ''' Create new index for the specified user '''
    data = {}
    return jsonify(data)

@PAGE.route("/es/update/<idx_id>/<user>/", methods=['GET','POST'])
@with_http_auth
def update_folder(idx_id, user):
    ''' Update folder '''
    data = {}
    return jsonify(data)

@PAGE.route("/es/get/<idx_id>/<user>/", methods=['GET','POST'])
@with_http_auth
def get_folder(idx_id, user):
    ''' Return folder contents '''
    data = {}
    return jsonify(data)