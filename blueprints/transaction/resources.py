import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import get_jwt_claims, jwt_required
from blueprints.transaction_details import *
from blueprints.seller import *

import datetime
import requests

bp_transaction = Blueprint('transaction', __name__)
api = Api(bp_transaction)


class TransactionResource(Resource):

    def __init__(self):
        pass

    @jwt_required
    def get(self, id=None):
        jwtClaims = get_jwt_claims()
        if (id == None):
            parser = reqparse.RequestParser()
            parser.add_argument('buyer_id', type=int, location='args')
            parser.add_argument('seller_id', type=int, location='args')
            parser.add_argument('p', type=int, location='args')
            parser.add_argument('rp', type=int, location='args')
            parser.add_argument('status_transaksi', type=int, location='args')
            args = parser.parse_args()
            qry = Transaction.query
        
            if (jwtClaims['status'] == 'seller'):
                qry = qry.filter_by(seller_id = jwtClaims['client_id'])
            
            if (jwtClaims['status'] == 'user'):
                qry = qry.filter_by(user_id = jwtClaims['client_id'])

            if (args['buyer_id'] is not None):
                qry = qry.filter_by(user_id = args['buyer_id'])
            
            if (args['seller_id'] is not None):
                qry = qry.filter_by(seller_id = args['seller_id'])
            
            if (args['status_transaksi'] is not None):
                qry = qry.filter_by(status_transaksi = args['status_transaksi'])

            rows = []
            if args['p'] is not None and args['rp'] is not None:
                offset = (args['p'] * args['rp']) - args['rp']
                for row in qry.limit(args['rp']).offset(offset).all():
                    rows.append(marshal(row, Transaction.response_fields))
            else:
                for row in qry.all():
                    rows.append(marshal(row, Transaction.response_fields))
            return {'status': 'oke', 'transaction': rows}, 200, {'Content-Type': 'application/json'}

        if Transaction.query.get(id) == None:
            return {'status': 'gagal', 'message': 'Transaksi ini tidak ada'}, 404, {'Content-Type': 'application/json'}
        if (jwtClaims['status'] == 'admin'):
            qry = Transaction.query.get(id)
            return {'status': 'oke', 'transaction': marshal(qry, Transaction.response_fields)}, 200, {'Content-Type': 'application/json'}
        elif (jwtClaims['status'] == 'seller') or (jwtClaims['status'] == 'user'):
            qry = Transaction.query
            if (qry.filter(Transaction.id == id).first().seller_id == jwtClaims['client_id']) or (qry.filter(Transaction.id == id).first().user_id == jwtClaims['client_id']):
                qry = Transaction.query.get(id)
                return {'status': 'oke', 'transaction': marshal(qry, Transaction.response_fields)}, 200, {'Content-Type': 'application/json'}
            return {'status': 'gagal', 'message': 'Anda tidak diperbolehkan melihat transaksi ini!'}, 401, {'Content-Type': 'application/json'}

# For Checkout
    @jwt_required
    def put(self, id):
        data_kota = str(Kota.query.all())
        jwtClaims = get_jwt_claims()
        user_id = jwtClaims['client_id']
        parser = reqparse.RequestParser()
        parser.add_argument('payment_method', location='json', required=True)
        parser.add_argument('alamat', location='json')
        parser.add_argument('kota', location='json', choices=data_kota)
        args = parser.parse_args()
        qry = Transaction.query.get(id)
        if qry.user_id != user_id:
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
        qry.payment_method = args['payment_method']
        if args['alamat'] is not None:
            qry.alamat = args['alamat']
        else:
            qry.alamat = User.query.filter(User.id == user_id).first.alamat
        if args['kota'] is not None:
            qry.kota = args['kota']
            qry.id_kota = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
        else:
            qry.kota = User.query.filter(User.id == user_id).first.kota
            qry.id_kota = User.query.filter(User.id == user_id).first.id_kota
        
        qry_id = TransactionDetail.query.filter(TransactionDetail.transaction_id == id).all()
        qry_id = marshal(qry_id, TransactionDetail.response_fields), 200, {'Content-Type': 'application/json'}
        seller_id = qry_id[0][0]['seller_id']
        seller_kota = Seller.query.filter(Seller.client_id == seller_id).first().id_kota
        qry.total_ongkir = self.hitungOngkir(seller_kota, qry.id_kota, qry.total_berat, 'jne')
        qry.status_transaksi = 1
        qry.updated_at = datetime.datetime.now()
        db.session.commit()
        if qry is not None:
            return marshal(qry, Transaction.response_fields), 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Transaction not found'}, 404, {'Content-Type': 'application/json'}

# Compute total and change transaction status 
    @jwt_required
    def patch(self, id):
        jwtClaims = get_jwt_claims()
        user_id = jwtClaims['client_id']
        parser = reqparse.RequestParser()
        parser.add_argument('status_transaksi', location='json')
        args = parser.parse_args()
        qry = Transaction.query.get(id)
        if qry is not None:
            if (args['status_transaksi'] is None):
                if qry.user_id != user_id:
                    return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
                qry_id = TransactionDetail.query.filter(TransactionDetail.transaction_id == id).all()
                qry_id = marshal(qry_id, TransactionDetail.response_fields), 200, {'Content-Type': 'application/json'}
                qry.total_item = 0
                qry.total_berat = 0
                qry.total_harga = 0
                for item in qry_id[0]:
                    qry.total_item += item['qty']
                    qry.total_berat += item['berat']
                    qry.total_harga += item['harga']

                if qry.total_berat >= 30000:
                    return {'status': 'gagal', 'message': 'Barang terlalu berat, pengiriman maksimal 30kg'}, 200, {'Content-Type': 'application/json'}
            elif (args['status_transaksi'] is not None):
                if (jwtClaims['status'] == 'admin' or jwtClaims['status']=='seller'):
                    qry.status_transaksi = args['status_transaksi']
                else:
                    return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
            db.session.commit()
            return {'status': 'oke', 'transaction': marshal(qry, Transaction.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Transaction not found'}, 404, {'Content-Type': 'application/json'}

    def hitungOngkir(self, origin, destination, weight, courier):
        host = 'https://api.rajaongkir.com/starter'
        headers = {'key': 'fe20e3f08b529d49f43143180513be36'}
        rq = requests.post(host + '/cost', headers = headers, data={'origin': origin, 'destination': destination, 'weight': weight, 'courier': courier})
        hasil = rq.json()
        return hasil['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
    
    def options(self, id=None):
        return {}, 200

api.add_resource(TransactionResource, '/<int:id>', '')