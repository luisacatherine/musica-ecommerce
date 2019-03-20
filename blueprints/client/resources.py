import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import jwt_required 

bp_client = Blueprint('client', __name__)
api = Api(bp_client)

class ClientResource(Resource):

    def __init__(self):
        pass

    # @jwt_required
    def get(self, client_id=None):
        if (client_id == None):
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=5)
            parser.add_argument('status', type=str, location='args')
            args = parser.parse_args()
            offset = (args['p'] * args['rp']) - args['rp']
            qry = Client.query
            
            if args['status'] is not None:
                qry = qry.filter_by(status=args['status'])

            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Client.response_fields))
            return rows, 200, {'Content-Type': 'application/json'}
        else:
            qry = Client.query.get(client_id) # select * from Client where id = id
            if qry is not None:
                return marshal(qry, Client.response_fields), 200, {'Content-Type': 'application/json'}
            return {'status': 'NOT_FOUND', 'message': 'Client not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def put(self, client_id):
        parser = reqparse.RequestParser()
        parser.add_argument('email', location='json')
        parser.add_argument('password', location='json')
        parser.add_argument('status', location='json', choices=['user', 'seller', 'admin'])
        args = parser.parse_args()
        qry = Client.query.get(client_id)
        if args['email'] is not None:
            qry.email = args['email']
        if args['password'] is not None:
            qry.password = args['password']
        if args['status'] is not None:
            qry.status = args['status']
        qry.updated_at = datetime.datetime.now()
        db.session.commit()
        if qry is not None:
            return marshal(qry, Client.response_fields), 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Client not found'}, 404, {'Content-Type': 'application/json'}

    # def delete(self, client_id):
    #     qry = Client.query.get(client_id)
    #     user = User.query.filter(User.client_id == client_id).first()
    #     if qry is not None:
    #         db.session.delete(qry)
    #         db.session.delete(user)
    #         db.session.commit()
    #         return 'deleted', 200, {'Content-Type': 'application/json'}
    #     else:
    #         return {'status': 'NOT_FOUND', 'message': 'Client not found'}, 404, {'Content-Type': 'application/json'}

api.add_resource(ClientResource, '/<int:client_id>', '')