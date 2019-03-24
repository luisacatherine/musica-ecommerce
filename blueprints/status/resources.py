import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required

bp_status = Blueprint('status', __name__)
api = Api(bp_status)

class StatusResource(Resource):

    def __init__(self):
        pass

    def get(self):
        qry = StatusTransaksi.query
        parser = reqparse.RequestParser()
        parser.add_argument('id', location='args')
        args = parser.parse_args()

        if args['id'] is not None:
            qry = StatusTransaksi.query.get(args['id'])
            return {'status': 'oke', 'status_transaksi': marshal(qry, StatusTransaksi.response_fields)}, 200, {'Content-Type': 'application/json'}

        rows = []
        for row in qry.all():
            rows.append(marshal(row, StatusTransaksi.response_fields))
        return {'status': 'oke', 'status_transaksi': rows}, 200, {'Content-Type': 'application/json'}
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('status', location='json')
        args = parser.parse_args()
        new_status = StatusTransaksi(None, args['status'])

        db.session.add(new_status)
        db.session.commit()
        return {'status': 'oke', 'status': marshal(new_status, StatusTransaksi.response_fields)}, 200, {'Content-Type': 'application/json'}
    
    def options(self):
        return {},200

api.add_resource(StatusResource, '')