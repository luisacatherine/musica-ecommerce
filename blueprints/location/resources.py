import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime

bp_provinsi = Blueprint('provinsi', __name__)
api = Api(bp_provinsi)

class ProvinsiResource(Resource):

    def __init__(self):
        pass
    def get(self):
        qry = Provinsi.query
        rows = []
        for row in qry.all():
            rows.append(marshal(row, Provinsi.response_fields))
        return {'status': 'oke', 'provinsi': rows}, 200, {'Content-Type': 'application/json'}
    
    def options(self):
        return {},200

api.add_resource(ProvinsiResource,'')

bp_kota = Blueprint('kota', __name__)
api = Api(bp_kota)

class KotaResource(Resource):

    def __init__(self):
        pass
    def get(self):
        data_provinsi = str(Provinsi.query.all())
        qry = Kota.query
        parser = reqparse.RequestParser()
        parser.add_argument('provinsi', location='args', choices=data_provinsi, required=True)
        args = parser.parse_args()

        qry = qry.filter_by(nama_provinsi = args['provinsi'])
        rows = []
        for row in qry.all():
            rows.append(marshal(row, Kota.response_fields))
        return {'status': 'oke', 'kota': rows}, 200, {'Content-Type': 'application/json'}
    
    def options(self):
        return {},200

api.add_resource(KotaResource, '')