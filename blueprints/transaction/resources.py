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
        for item in qry_id[0]:
            qry.total_item += item['qty']
            qry.total_berat += item['berat']
            qry.total_harga += item['harga']
        
        seller_id = qry_id[0][0]['seller_id']
        seller_kota = Seller.query.filter(Seller.client_id == seller_id).first().id_kota
        qry.total_ongkir = self.hitungOngkir(seller_kota, qry.id_kota, qry.total_berat, 'jne')
        qry.updated_at = datetime.datetime.now()
        db.session.commit()
        if qry is not None:
            return marshal(qry, Transaction.response_fields), 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'NOT_FOUND', 'message': 'Transaction not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        user_id = jwtClaims['client_id']
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()
        transaction = Transaction(None, ' ', user_id, ' ', ' ', 0, 0, 0, 0, 0, 0, created_at, updated_at)
        db.session.add(transaction)
        db.session.commit()
        return marshal(transaction, Transaction.response_fields), 200, {'Content-Type': 'application/json'}

    def hitungOngkir(self, origin, destination, weight, courier):
        host = 'https://api.rajaongkir.com/starter'
        headers = {'key': 'fe20e3f08b529d49f43143180513be36'}
        rq = requests.post(host + '/cost', headers = headers, data={'origin': origin, 'destination': destination, 'weight': weight, 'courier': courier})
        hasil = rq.json()
        return hasil['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']

api.add_resource(TransactionResource, '/<int:id>', '')