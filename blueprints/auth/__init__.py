import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from blueprints.client import *
from passlib.hash import sha256_crypt

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResources(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        # qry = Client.query.filter_by(email=args['email']).filter_by(password=args['password']).first()
        qry = Client.query.filter_by(email=args['email']).first()
        if qry is None:
            return {'status': 'UNAUTHORIZED', 'message': 'Anda belum terdaftar!'}, 401
        temp = Client.query.filter(Client.email == args['email']).first().password

        if (sha256_crypt.verify(args['password'], temp) == True):
            token = create_access_token(marshal(qry, Client.response_fields))
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'Password Anda salah!'}, 401
        return {'status': 'oke', 'token': token}, 200

api.add_resource(CreateTokenResources, '')