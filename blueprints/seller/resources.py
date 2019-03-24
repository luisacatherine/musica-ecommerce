import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
from passlib.hash import sha256_crypt

bp_seller = Blueprint('seller', __name__)
api = Api(bp_seller)

class SellerResource(Resource):

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
                qry = Seller.query

                if args['kota'] is not None:
                    qry = qry.filter(Seller.kota.ilike('%{}%'.format(args['kota'])))

                if args['gender'] is not None:
                    qry = qry.filter_by(gender=args['gender'])

                rows = []
                for row in qry.limit(args['rp']).offset(offset).all():
                    rows.append(marshal(row, Seller.response_fields))
                return {'status': 'oke', 'seller': rows}, 200, {'Content-Type': 'application/json'}
            else:
                qry = Seller.query.get(id) # select * from Client where id = id
                if qry is not None:
                    return {'status': 'oke', 'seller': marshal(qry, Seller.response_fields)}, 200, {'Content-Type': 'application/json'}
                return {'status': 'NOT_FOUND', 'message': 'Seller not found'}, 404, {'Content-Type': 'application/json'}
        else:
            qry = Seller.query.filter(Seller.client_id == jwtClaims['client_id']).first()
            return {'status': 'oke', 'seller': marshal(qry, Seller.response_fields)}, 200, {'Content-Type': 'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'seller' and jwtClaims['status'] != 'admin':
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
        if jwtClaims['status'] == 'seller':
            id = Seller.query.filter(Seller.client_id == jwtClaims['client_id']).first().id
        data_kota = str(Kota.query.all())
        data_provinsi = str(Provinsi.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('date_of_birth', location='json')
        parser.add_argument('gender', location='json', choices=['m', 'f'])
        parser.add_argument('phone_number', location='json')
        parser.add_argument('alamat', location='json')
        parser.add_argument('provinsi', location='json', choices=data_provinsi)
        parser.add_argument('kota', location='json', choices=data_kota)
        parser.add_argument('bank', location='json', choices=['BCA', 'Mandiri', 'BNI', 'BRI', 'BTPN'])
        parser.add_argument('no_rekening', location='json')
        args = parser.parse_args()
        qry = Seller.query.get(id)
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
            if args['bank'] is not None:
                qry.bank = args['bank']
            if args['no_rekening'] is not None:
                qry.no_rekening = args['no_rekening']
            qry.updated_at = datetime.datetime.now()
            db.session.commit()
            return {'status': 'oke', 'seller': marshal(qry, Seller.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Seller not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        status = get_jwt_claims()['status']
        if (status == 'admin'):
            qry = Seller.query.get(id)
            client = Client.query.filter(Client.client_id == (Seller.query.filter(Seller.id == id).first().client_id)).first()
            product = Items.query.filter(Items.id_penjual == (Seller.query.filter(Seller.id == id).first().client_id)).all()
            if qry is not None:
                db.session.delete(qry)
                db.session.delete(client)
                db.session.delete(product)
                db.session.commit()
                return {'status': 'deleted'}, 200, {'Content-Type': 'application/json'}
            else:
                return {'status': 'NOT_FOUND', 'message': 'Seller not found'}, 404, {'Content-Type': 'application/json'}
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
        parser.add_argument('bank', location='json', choices=['BCA', 'Mandiri', 'BNI', 'BRI', 'BTPN'], required=True)
        parser.add_argument('no_rekening', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('photo_url', location='json')
        args = parser.parse_args()
        if Client.query.filter(Client.email == args['email']).first() is not None:
            return {'message': 'This email is already registered, please use another email'}, 500, {'Content-Type': 'application/json'}
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        client = Client(None, args['email'], sha256_crypt.encrypt(args['password']), 'seller', args['created_at'], args['updated_at'])
        db.session.add(client)
        db.session.commit()
        args['client_id'] = Client.query.filter(Client.email == args['email']).first().client_id
        args['id_kota'] = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        seller = Seller(None, args['name'], args['date_of_birth'], args['gender'], args['phone_number'], args['alamat'], args['provinsi'], args['kota'], args['id_kota'], args['bank'], args['no_rekening'], args['client_id'], args['photo_url'], args['created_at'], args['updated_at'])
        db.session.add(seller)
        db.session.commit()
        return {'status': 'oke', 'seller': marshal(seller, Seller.response_fields)}, 200, {'Content-Type': 'application/json'}
    
    def options(self, id=None):
        return {},200

api.add_resource(SellerResource, '/<int:id>', '')