'''
Created on Jan 2, 2013

@author: olav
'''

from flask import Blueprint
from flask import jsonify
from flask import abort

from conf.security import with_http_auth
from conf.security import disallow_special_characters
from services.folder_service import FolderService
from services.es_service import EsService
from domain.user import User

PAGE = Blueprint('es_page', __name__)

@PAGE.route("/es", methods=['GET', 'POST'])
@with_http_auth
def index():
    ''' Show status '''
    es = EsService()
    return jsonify(es.get_status())

@PAGE.route("/es/<uid>", methods=['GET', 'POST'])
@with_http_auth
def listall(uid):
    ''' List data from the specified user '''
    user = User.get(uid)
    data = FolderService(user).find_all()
    return jsonify(data)

@PAGE.route("/es/create/<uid>/", methods=['GET', 'POST'])
@disallow_special_characters
@with_http_auth
def create(uid):
    ''' Create new index for the specified user and fill it with content'''
    user = User.get(uid)
    if user:
        eserver = EsService()
        results = eserver.create_index(user.uid, overwrite=True)
        if results['status'] != 200:
            abort(404)
        folder_service = FolderService(user)
        folders = folder_service.find_all()
        return jsonify(dict(status='ok'))
    abort(404)

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