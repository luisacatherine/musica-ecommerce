import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
import requests

bp_transdetail = Blueprint('transdetail', __name__)
api = Api(bp_transdetail)

class TransactionDetailResource(Resource):

    def __init__(self):
        pass

    @jwt_required
    def get(self):
        jwtClaims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('buyer_id', location='args', type=int)
        parser.add_argument('transaction', location='args', type=int)
        args = parser.parse_args()
        qry = TransactionDetail.query
        if args['transaction'] is not None:
            qry = qry.filter_by(transaction_id = args['transaction'])
        
        rows = []
        for row in qry.all():
            rows.append(marshal(row, TransactionDetail.response_fields))
        return {'status': 'oke', 'transaction_details': rows}, 200, {'Content-Type': 'application/json'}

    
    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location='json', required=True, type=int)
        parser.add_argument('qty', location='json', default=1, type=int)
        args = parser.parse_args()
        qry = Items.query.get(args['product_id'])
        if qry is None:
            return {'status': 'gagal', 'message': 'Barang tidak ditemukan'}, 200, {'Content-Type': 'application/json'}
        stok = Items.query.filter(Items.id == args['product_id']).first().stok
        status_order = Items.query.filter(Items.id == args['product_id']).first().status
        if status_order == 'ready' and args['qty'] > stok:
            return {'status': 'gagal', 'message': 'Stok tidak cukup'}, 200, {'Content-Type': 'application/json'}
        buyer_id = jwtClaims['client_id']
        cek_transaksi = Transaction.query.filter(Transaction.status_transaksi == 0).filter(Transaction.user_id == buyer_id).first()
        if cek_transaksi is None:
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            transaction = Transaction(None, ' ', buyer_id, 0, ' ', ' ', 0, 0, 0, 0, 0, 0, created_at, updated_at)
            db.session.add(transaction)
            db.session.commit()
        transaction_id = Transaction.query.filter(Transaction.status_transaksi == 0).filter(Transaction.user_id == buyer_id).first().id
        qry = Transaction.query.get(transaction_id)
        seller_id = Items.query.filter(Items.id == args['product_id']).first().id_penjual
        if qry.seller_id == 0:
            qry.seller_id = seller_id
            db.session.commit()
        else:
            if qry.seller_id != seller_id:
                return {'status': 'gagal', 'message': 'Anda masih memiliki transaksi yang belum terselesaikan dengan penjual lain!'}, 200, {'Content-Type': 'application/json'}
        berat = args['qty'] * Items.query.filter(Items.id == args['product_id']).first().berat
        harga = args['qty'] * Items.query.filter(Items.id == args['product_id']).first().harga_promo
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        transaction = TransactionDetail(None, transaction_id, args['product_id'], seller_id, buyer_id, args['qty'], harga, berat, args['created_at'], args['updated_at'])
        db.session.add(transaction)
        db.session.commit()
        qry = Items.query.filter(Items.id == args['product_id']).first()
        qry.stok -= args['qty']
        db.session.commit()
        return {'status': 'oke', 'transaksi': marshal(transaction, TransactionDetail.response_fields)}, 200, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        qry = TransactionDetail.query.get(id)
        if qry is None:
            return {'status': 'gagal', 'message': 'Transaksi ini tidak ada!'}, 200, {'Content-Type': 'application/json'}
        if jwtClaims['status'] == 'user' or jwtClaims['status'] == 'seller':
            if jwtClaims['client_id'] != qry.buyer_id:
                return {'status': 'gagal', 'message': 'Transaksi ini bukan milik Anda!'}, 200, {'Content-Type': 'application/json'}
        item = Items.query.filter(Items.id == qry.product_id).first()
        transaction = Transaction.query.filter(Transaction.id == qry.transaction_id).first()
        if(transaction.total_item == qry.qty):
            db.session.delete(transaction)
        else:
            transaction.total_item -= qry.qty
        item.stok += qry.qty
        db.session.delete(qry)
        db.session.commit()
        return {'status': 'deleted'}, 200, {'Content-Type': 'application/json'}
    
    def options(self, id=None):
        return {}, 200

api.add_resource(TransactionDetailResource, '/<int:id>', '')