import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime

bp_user = Blueprint('user', __name__)
api = Api(bp_user)


class UserResource(Resource):

    def __init__(self):
        pass
    
    @jwt_required
    def get(self, id=None):
        if (id == None):
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args', default=1)
            parser.add_argument('rp', type=int, location='args', default=5)
            parser.add_argument('kota', type=str, location='args')
            parser.add_argument('gender', type=str, location='args')
            args = parser.parse_args()
            offset = (args['p'] * args['rp']) - args['rp']
            qry = User.query

            if args['kota'] is not None:
                qry = qry.filter_by(kota=args['kota'])
            
            if args['gender'] is not None:
                qry = qry.filter_by(gender=args['gender'])

            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, User.response_fields))
            return rows, 200, {'Content-Type': 'application/json'}
        else:
            qry = User.query.get(id) # select * from Client where id = id
            if qry is not None:
                return marshal(qry, User.response_fields), 200, {'Content-Type': 'application/json'}
            return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        data_kota = str(Kota.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('age', location='json')
        parser.add_argument('gender', location='json', choices=['m', 'f'])
        parser.add_argument('email', location='json')
        parser.add_argument('alamat', location='json')
        parser.add_argument('kota', location='json', choices=data_kota)
        parser.add_argument('client_id', location='json')
        args = parser.parse_args()
        qry = User.query.get(id)
        if args['name'] is not None:
            qry.name = args['name']
        if args['age'] is not None:
            qry.age = args['age']
        if args['gender'] is not None:
            qry.gender = args['gender']
        if args['email'] is not None:
            qry.email = args['email']
        if args['alamat'] is not None:
            qry.alamat = args['alamat']
        if args['kota'] is not None:
            qry.kota = args['kota']
            qry.id_kota = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        qry.client_id = jwtClaims['client_id']
        qry.updated_at = datetime.datetime.now()
        db.session.commit()
        if qry is not None:
            return marshal(qry, User.response_fields), 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        qry = User.query.get(id)
        if qry is not None:
            db.session.delete(qry)
            db.session.commit()
            return 'deleted', 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        data_kota = str(Kota.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('age', location='json', required=True, type=int)
        parser.add_argument('gender', location='json', choices=['m', 'f'], required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
        parser.add_argument('kota', location='json', choices=data_kota, required=True)
        args = parser.parse_args()
        args['client_id'] = jwtClaims['client_id']
        args['id_kota'] = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        user = User(None, args['name'], args['age'], args['gender'], args['email'], args['alamat'], args['kota'], args['id_kota'], args['client_id'], args['created_at'], args['updated_at'])
        db.session.add(user)
        db.session.commit()
        return marshal(user, User.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(UserResource, '/<int:id>', '')