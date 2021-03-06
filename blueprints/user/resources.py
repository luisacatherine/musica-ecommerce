import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
from passlib.hash import sha256_crypt

bp_user = Blueprint('user', __name__)
api = Api(bp_user)

class UserResource(Resource):

    def __init__(self):
        pass
    
    @jwt_required
    def get(self, id=None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] == 'admin':
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
                return {'status': 'oke', 'user': rows}, 200, {'Content-Type': 'application/json'}
            else:
                qry = User.query.get(id) # select * from Client where id = id
                if qry is not None:
                    return {'status': 'oke', 'user': marshal(qry, User.response_fields)}, 200, {'Content-Type': 'application/json'}
                return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}
        else:
            qry = User.query.filter(User.client_id == jwtClaims['client_id']).first()
            return marshal(qry, User.response_fields), 200, {'Content-Type': 'application/json'}

    
    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user' and jwtClaims['status'] != 'admin':
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
        if jwtClaims['status'] == 'user':
            id = User.query.filter(User.client_id == jwtClaims['client_id']).first().id
        data_kota = str(Kota.query.all())
        data_provinsi = str(Provinsi.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('date_of_birth', location='json', type=int)
        parser.add_argument('gender', location='json', choices=['m', 'f'])
        parser.add_argument('phone_number', location='json')
        parser.add_argument('alamat', location='json')
        parser.add_argument('provinsi', location='json', choices=data_provinsi)
        parser.add_argument('kota', location='json', choices=data_kota)
        args = parser.parse_args()
        qry = User.query.get(id)
        if qry is not None:
            if args['name'] is not None:
                qry.name = args['name']
            if args['date_of_birth'] is not None:
                qry.date_of_birth = args['date_of_birth']
            if args['gender'] is not None:
                qry.gender = args['gender']
            if args['phone_number'] is not None:
                qry.phone_number = args['phone_number']
            if args['alamat'] is not None:
                qry.alamat = args['alamat']
            if args['provinsi'] is not None:
                qry.provinsi = args['provinsi']
            if args['kota'] is not None:
                qry.kota = args['kota']
                qry.id_kota = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
            if args['photo_url'] is not None:
                qry.photo_url = args['photo_url']
            qry.client_id = jwtClaims['client_id']
            qry.updated_at = datetime.datetime.now()
            db.session.commit()
            return {'status': 'oke', 'user': marshal(qry, User.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        status = get_jwt_claims()['status']
        if (status == 'admin'):
            qry = User.query.get(id)
            client = Client.query.filter(Client.client_id == (User.query.filter(User.id == id).first().client_id)).first()
            if qry is not None:
                db.session.delete(qry)
                db.session.delete(client)
                db.session.commit()
                return {'status': 'deleted'}, 200, {'Content-Type': 'application/json'}
            else:
                return {'status': 'NOT_FOUND', 'message': 'User not found'}, 404, {'Content-Type': 'application/json'}
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}

    def post(self):
        data_kota = str(Kota.query.all())
        data_provinsi = str(Provinsi.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('date_of_birth', location='json', required=True)
        parser.add_argument('gender', location='json', choices=['m', 'f'], required=True)
        parser.add_argument('phone_number', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
        parser.add_argument('provinsi', location='json', choices=data_provinsi, required=True)
        parser.add_argument('kota', location='json', choices=data_kota, required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('photo_url', location='json')
        args = parser.parse_args()
        if Client.query.filter(Client.email == args['email']).first() is not None:
            return {'message': 'This email is already registered, please use another email'}, 500, {'Content-Type': 'application/json'}
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        client = Client(None, args['email'], sha256_crypt.encrypt(args['password']), 'user', args['created_at'], args['updated_at'])
        db.session.add(client)
        db.session.commit()
        args['client_id'] = Client.query.filter(Client.email == args['email']).first().client_id
        args['id_kota'] = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        user = User(None, args['name'], args['date_of_birth'], args['gender'], args['phone_number'], args['alamat'], args['provinsi'], args['kota'], args['id_kota'], args['client_id'], args['photo_url'], args['created_at'], args['updated_at'])
        db.session.add(user)
        db.session.commit()
        return {'status': 'oke', 'user': marshal(user, User.response_fields)}, 200, {'Content-Type': 'application/json'}

api.add_resource(UserResource, '/<int:id>', '')