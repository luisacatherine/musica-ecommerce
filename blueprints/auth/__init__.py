import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from blueprints.client import *

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResources(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('client_key', location='json', required=True)
        parser.add_argument('client_secret', location='json', required=True)
        args = parser.parse_args()

        qry = Client.query.filter_by(client_key=args['client_key']).filter_by(client_secret=args['client_secret']).first()
        if qry is not None:
            token = create_access_token(marshal(qry, Client.response_fields))
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'invalid key'}, 401
        return {'token': token}, 200

api.add_resource(CreateTokenResources, '')