import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
from passlib.hash import sha256_crypt

bp_user_public = Blueprint('user_public', __name__)
api = Api(bp_user_public)

class UserPublic(Resource):

    def __init__(self):
        pass
    
    def get(self, id=None):
        qry = User.query.filter(User.client_id == id).first()
        if qry is not None:
            name = qry.name,
            kota = qry.kota,
            client_id = qry.client_id
            photo_url = qry.photo_url
            return {'status': 'oke', 'user': {'name': qry.name, 'kota': qry.kota, 'client_id': qry.client_id, 'photo_url': qry.photo_url}}, 200, {'Content-Type': 'application/json'}
        return {'status': 'gagal', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}
    
    def options(self):
        return {},200

api.add_resource(UserPublic, '/<int:id>', '')