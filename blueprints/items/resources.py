import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime

bp_item = Blueprint('item', __name__)
api = Api(bp_item)


class ItemsResource(Resource):

    def __init__(self):
        pass
    
    # @jwt_required
    # def get(self, id=None):
    #     if (id == None):
    #         parser = reqparse.RequestParser()
    #         parser.add_argument('p', type=int, location='args', default=1)
    #         parser.add_argument('rp', type=int, location='args', default=5)
    #         parser.add_argument('kota', type=str, location='args')
    #         parser.add_argument('gender', type=str, location='args')
    #         args = parser.parse_args()
    #         offset = (args['p'] * args['rp']) - args['rp']
    #         qry = Items.query

    #         if args['kota'] is not None:
    #             qry = qry.filter(Items.kota.ilike('%{}%'.format(args['kota'])))

    #         if args['gender'] is not None:
    #             qry = qry.filter_by(gender=args['gender'])

    #         rows = []
    #         for row in qry.limit(args['rp']).offset(offset).all():
    #             rows.append(marshal(row, Items.response_fields))
    #         return rows, 200, {'Content-Type': 'application/json'}
    #     else:
    #         qry = Items.query.get(id) # select * from Client where id = id
    #         if qry is not None:
    #             return marshal(qry, Items.response_fields), 200, {'Content-Type': 'application/json'}
    #         return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
    
    # @jwt_required
    # def put(self, id):
    #     jwtClaims = get_jwt_claims()
    #     data_kota = str(Kota.query.all())
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('name', location='json')
    #     parser.add_argument('age', location='json', type=int)
    #     parser.add_argument('gender', location='json', choices=['m', 'f'])
    #     parser.add_argument('alamat', location='json')
    #     parser.add_argument('kota', location='json', choices=data_kota)
    #     args = parser.parse_args()
    #     qry = Items.query.get(id)
    #     if args['name'] is not None:
    #         qry.name = args['name']
    #     if args['age'] is not None:
    #         qry.age = args['age']
    #     if args['gender'] is not None:
    #         qry.gender = args['gender']
    #     if args['alamat'] is not None:
    #         qry.alamat = args['alamat']
    #     if args['kota'] is not None:
    #         qry.kota = args['kota']
    #         qry.id_kota = Kota.query.filter(Kota.nama_kota == args['kota']).first().id
    #     qry.client_id = jwtClaims['client_id']
    #     qry.updated_at = datetime.datetime.now()
    #     db.session.commit()
    #     if qry is not None:
    #         return marshal(qry, Items.response_fields), 200, {'Content-Type': 'application/json'}
    #     else:
    #         return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}

    # @jwt_required
    # def delete(self, id):
    #     qry = Items.query.get(id)
    #     client = Client.query.filter(Client.client_id == (Items.query.filter(Items.id == id).first().client_id)).first()
    #     if qry is not None:
    #         db.session.delete(qry)
    #         db.session.delete(client)
    #         db.session.commit()
    #         return 'deleted', 200, {'Content-Type': 'application/json'}
    #     else:
    #         return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        data_kategori = str(Category.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('kategori', location='json', required=True, choices=data_kategori)
        parser.add_argument('nama', location='json', required=True)
        parser.add_argument('merk', location='json', required=False)
        parser.add_argument('harga', type=int, location='json', required=True)
        parser.add_argument('status', location='json', required=True, choices=['ready', 'pre-order'])
        parser.add_argument('stok', location='json', type=int)
        parser.add_argument('deskripsi_produk', location='json')
        parser.add_argument('berat', location='json', required=True, type=int)
        parser.add_argument('promo', location='json', type=bool)
        parser.add_argument('harga_promo', type=int, location='json')
        parser.add_argument('show', location='json', type=bool)
        args = parser.parse_args()
        if args['promo'] is None:
            args['harga_promo'] = args['harga']
        if args['status'] == 'pre-order':
            args['stok'] = -1
        args['id_penjual'] = jwtClaims['client_id']
        args['id_kategori'] = Category.query.filter(Category.nama_kategori == args['kategori']).first().id
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        items = Items(None, args['id_penjual'], args['id_kategori'], args['nama'], args['merk'], args['harga'], args['status'], args['stok'], args['deskripsi_produk'], args['berat'], args['promo'], args['harga_promo'], args['show'], args['created_at'], args['updated_at'])
        db.session.add(items)
        db.session.commit()
        return marshal(items, Items.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(ItemsResource, '/<int:id>', '')