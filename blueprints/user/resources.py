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
                qry = qry.filter(User.kota.ilike('%{}%'.format(args['kota'])))

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
        parser.add_argument('age', location='json', type=int)
        parser.add_argument('gender', location='json', choices=['m', 'f'])
        parser.add_argument('alamat', location='json')
        parser.add_argument('kota', location='json', choices=data_kota)
        args = parser.parse_args()
        qry = User.query.get(id)
        if args['name'] is not None:
            qry.name = args['name']
        if args['age'] is not None:
            qry.age = args['age']
        if args['gender'] is not None:
            qry.gender = args['gender']
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
        client = Client.query.filter(Client.client_id == (User.query.filter(User.id == id).first().client_id)).first()
        if qry is not None:
            db.session.delete(qry)
            db.session.delete(client)
            db.session.commit()
            return 'deleted', 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}

    def post(self):
        data_kota = str(Kota.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('age', location='json', required=True, type=int)
        parser.add_argument('gender', location='json', choices=['m', 'f'], required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
        parser.add_argument('kota', location='json', choices=data_kota, required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()
        if Client.query.filter(Client.email == args['email']).first() is not None:
            return {'message': 'This email is already registered, please use another email'}, 500, {'Content-Type': 'application/json'}
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        client = Client(None, args['email'], args['password'], 'user', args['created_at'], args['updated_at'])
        db.session.add(client)
        db.session.commit()
        args['cart'] = 0
        args['client_id'] = Client.query.filter(Client.email == args['email']).first().client_id
        args['id_kota'] = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        user = User(None, args['name'], args['age'], args['gender'], args['alamat'], args['kota'], args['id_kota'], args['client_id'], args['cart'], args['created_at'], args['updated_at'])
        db.session.add(user)
        db.session.commit()
        return marshal(user, User.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(UserResource, '/<int:id>', '')