import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
from datetime import timedelta

bp_category = Blueprint('category', __name__)
api = Api(bp_category)

class CategoryResource(Resource):

    def __init__(self):
        pass
    
    def get(self, id=None):
        if (id == None):
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=20)
            parser.add_argument('q', type=int, location='args')
            args = parser.parse_args()              

            offset = (args['p'] * args['rp']) - args['rp']
            qry = Category.query
            if args['q'] is not None:
                qry = qry.limit(args['q'])

            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Category.response_fields))
            return {'status': 'oke', 'kategori': rows}, 200, {'Content-Type': 'application/json'}
        else:
            qry = Category.query.get(id) # select * from Client where id = id
            if qry is not None:
                return {'status': 'oke', 'kategori': marshal(qry, Category.response_fields)}, 200, {'Content-Type': 'application/json'}
            return {'status': 'NOT_FOUND', 'message': 'Category not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        qry = Category.query.get(id)
        parser = reqparse.RequestParser()
        parser.add_argument('nama_kategori', location='json')
        parser.add_argument('url', location='json')
        parser.add_argument('url_besar', location='json')
        args = parser.parse_args()
        if jwtClaims['status'] == 'admin':
            args['updated_at'] = datetime.datetime.now()
            if args['nama_kategori'] is not None:
                qry.nama_kategori = args['nama_kategori']
            if args['url'] is not None:
                qry.url = args['url']
            if args['url_besar'] is not None:
                qry.url_besar = args['url_besar']
            db.session.commit()
            return {'status': 'oke', 'kategori': marshal(qry, Category.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'gagal', 'message': 'Anda bukan admin, tidak diizinkan melakukan tindakan ini!'}, 401, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('nama_kategori', location='json', required=True)
        parser.add_argument('url', location='json', required=True)
        parser.add_argument('url_besar', location='json', required=True)
        args = parser.parse_args()
        if jwtClaims['status'] == 'admin':
            args['created_at'] = datetime.datetime.now()
            args['updated_at'] = datetime.datetime.now()
            kategori = Category(None, args['nama_kategori'], args['url'], args['url_besar'], args['created_at'], args['updated_at'])
            db.session.add(kategori)
            db.session.commit()
            return {'status': 'oke', 'kategori': marshal(kategori, Category.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'gagal', 'message': 'Anda bukan admin, tidak diizinkan melakukan tindakan ini!'}, 401, {'Content-Type': 'application/json'}

    def options(self, id=None):
        return {}, 200

api.add_resource(CategoryResource, '/<int:id>', '')