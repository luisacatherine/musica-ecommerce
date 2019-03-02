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

    def get(self, client_id=None):
        if (client_id == None):
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=5)
            parser.add_argument('client_id', type=int, location='args')
            parser.add_argument('status', type=int, location='args')
            args = parser.parse_args()
            offset = (args['p'] * args['rp']) - args['rp']
            qry = Client.query

            if args['client_id'] is not None:
                qry = qry.filter_by(client_id=args['client_id'])
            
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

    def put(self, client_id):
        parser = reqparse.RequestParser()
        parser.add_argument('client_id', location='json')
        parser.add_argument('client_key', location='json')
        parser.add_argument('client_secret', location='json')
        parser.add_argument('status', location='json')
        args = parser.parse_args()
        qry = Client.query.get(client_id)
        qry.client_key = args['client_key']
        qry.client_secret = args['client_secret']
        qry.status = args['status']
        db.session.commit()
        if qry is not None:
            return marshal(qry, Client.response_fields), 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Client not found'}, 404, {'Content-Type': 'application/json'}

    def delete(self, client_id):
        qry = Client.query.get(client_id)
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'deleted', 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Client not found'}, 404, {'Content-Type': 'application/json'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('client_key', location='json', required=True)
        parser.add_argument('client_secret', location='json', required=True)
        parser.add_argument('status', location='json', required=True)
        args = parser.parse_args()
        client = Client(None, args['client_key'], args['client_secret'], args['status'])
        db.session.add(client)
        db.session.commit()
        return marshal(client, Client.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(ClientResource, '/<int:client_id>', '')
