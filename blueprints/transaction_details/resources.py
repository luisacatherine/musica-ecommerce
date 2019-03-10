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
    def post(self):
        jwtClaims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location='json', required=True, type=int)
        parser.add_argument('qty', location='json', required=True, type=int)
        args = parser.parse_args()
        qry = Items.query.get(args['product_id'])
        if qry is None:
            return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
        buyer_id = jwtClaims['client_id']
        transaction_id = Transaction.query.filter(Transaction.status_transaksi == 0).filter(Transaction.user_id == buyer_id).first().id
        seller_id = Items.query.filter(Items.id == args['product_id']).first().id_penjual
        berat = args['qty'] * Items.query.filter(Items.id == args['product_id']).first().berat
        harga = args['qty'] * Items.query.filter(Items.id == args['product_id']).first().harga_promo
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        transaction = TransactionDetail(None, transaction_id, args['product_id'], seller_id, buyer_id, args['qty'], harga, berat, args['created_at'], args['updated_at'])
        db.session.add(transaction)
        db.session.commit()
        return marshal(transaction, TransactionDetail.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(TransactionDetailResource, '/<int:id>', '')