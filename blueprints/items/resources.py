import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime
from datetime import timedelta

bp_item = Blueprint('item', __name__)
api = Api(bp_item)

class ItemsResource(Resource):

    def __init__(self):
        pass
    
    def get(self, id=None):
        if (id == None):
            data_kategori = str(Category.query.all())
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location='args')
            parser.add_argument('rp', type=int, location='args')
            parser.add_argument('q', type=int, location='args')
            parser.add_argument('kategori', type=str, location='args')
            parser.add_argument('promo', location='args', type=bool)
            parser.add_argument('new_arrival', location='args', type=bool)
            parser.add_argument('status', location='args', choices=['ready', 'pre-order'])
            parser.add_argument('lokasi', location='args')
            parser.add_argument('nama', location='args')
            parser.add_argument('seller_id', location='args')
            parser.add_argument('excluded_id', location='args', type=int)
            parser.add_argument('harga_min', location='args', type=int)
            parser.add_argument('harga_max', location='args', type=int)
            parser.add_argument('sortby', location='args')
            parser.add_argument('showall', location='args', type=bool)
            args = parser.parse_args()
            
            qry = Items.query

            if args['showall'] is None:
                qry = qry.filter_by(show=True)

            if args['kategori'] is not None:
                temp = Category.query.filter(Category.nama_kategori == args['kategori']).first().id
                qry = qry.filter_by(id_kategori=temp)

            if args['promo'] is not None:
                qry = qry.filter_by(promo=args['promo'])

            if args['new_arrival'] == True:
                now = datetime.datetime.now()
                three_days = now - timedelta(days=7)
                qry = qry.filter(Items.created_at > three_days).filter(Items.created_at < now)

            if args['status'] is not None:
                qry = qry.filter_by(status=args['status'])

            if args['lokasi'] is not None:
                qry = qry.filter(Items.seller_city.ilike('%{}%'.format(args['lokasi'])))
            
            if args['nama'] is not None:
                qry = qry.filter(Items.nama.ilike('%{}%'.format(args['nama'])))

            if args['excluded_id'] is not None:
                qry = qry.filter(Items.id != args['excluded_id'])
            
            if args['harga_min'] is not None:
                qry = qry.filter(Items.harga_promo > args['harga_min'])

            if args['harga_max'] is not None:
                qry = qry.filter(Items.harga_promo < args['harga_max'])

            if args['seller_id'] is not None:
                qry = qry.filter_by(id_penjual=args['seller_id'])
            
            if args['sortby'] == 'hargamin':
                qry = qry.order_by(Items.harga_promo)
            elif args['sortby'] == 'hargamax':
                qry = qry.order_by(Items.harga_promo.desc())
            elif args['sortby'] == 'new':
                qry = qry.order_by(Items.updated_at.desc())

            if args['q'] is not None:
                qry = qry.limit(args['q'])

            rows = []

            if args['p'] is not None and args['rp'] is not None:
                offset = (args['p'] * args['rp']) - args['rp']
                for row in qry.limit(args['rp']).offset(offset).all():
                    temp = marshal(row, Items.response_fields)
                    item_seller = Seller.query.filter(Seller.client_id == row.id_penjual).first()
                    item_category = Category.query.filter(Category.id == row.id_kategori).first()
                    temp['item_seller'] = marshal(item_seller, Seller.response_fields)
                    temp['item_category'] = marshal(item_category, Category.response_fields)
                    rows.append(temp)
            else:
                for row in qry.all():
                    temp = marshal(row, Items.response_fields)
                    item_seller = Seller.query.filter(Seller.client_id == row.id_penjual).first()
                    item_category = Category.query.filter(Category.id == row.id_kategori).first()
                    temp['item_seller'] = marshal(item_seller, Seller.response_fields)
                    temp['item_category'] = marshal(item_category, Category.response_fields)
                    rows.append(temp) 
            return {'status': 'oke', 'items': rows}, 200, {'Content-Type': 'application/json'}
        else:
            qry = Items.query.get(id) # select * from Client where id = id
            if qry is not None:
                temp = marshal(qry, Items.response_fields)
                item_seller = Seller.query.filter(Seller.client_id == qry.id_penjual).first()
                item_category = Category.query.filter(Category.id == qry.id_kategori).first()
                temp['item_seller'] = marshal(item_seller, Seller.response_fields)
                temp['item_category'] = marshal(item_category, Category.response_fields)
                return {'status': 'oke', 'items': temp}, 200, {'Content-Type': 'application/json'}
            return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
    
    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] == 'seller' or jwtClaims['status'] == 'admin':
            data_kategori = str(Category.query.all())
            parser = reqparse.RequestParser()
            parser.add_argument('kategori', location='json', choices=data_kategori)
            parser.add_argument('nama', location='json')
            parser.add_argument('merk', location='json')
            parser.add_argument('harga', type=int, location='json')
            parser.add_argument('status', location='json', choices=['ready', 'pre-order'])
            parser.add_argument('stok', location='json', type=int)
            parser.add_argument('deskripsi_produk', location='json')
            parser.add_argument('berat', location='json', type=int)
            parser.add_argument('promo', location='json', type=bool)
            parser.add_argument('harga_promo', type=int, location='json')
            parser.add_argument('show', location='json', type=bool)
            parser.add_argument('photo_url', location='json')
            args = parser.parse_args()
            qry = Items.query.get(id)
            if qry is not None:
                if jwtClaims['status'] == 'seller':
                    if qry.id_penjual != jwtClaims['client_id']:
                        return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
                if args['kategori'] is not None:
                    if args['kategori'] != '':
                        qry.id_kategori = Category.query.filter(Category.nama_kategori == args['kategori']).first().id
                if args['nama'] is not None:
                    qry.nama = args['nama']
                if args['merk'] is not None:
                    qry.merk = args['merk']
                if args['harga'] is not None:
                    qry.harga = args['harga']
                if args['status'] is not None:
                    qry.status = args['status']
                if args['stok'] is not None:
                    qry.stok = args['stok']
                if args['deskripsi_produk'] is not None:
                    qry.deskripsi_produk = args['deskripsi_produk']
                if args['berat'] is not None:
                    qry.berat = args['berat']
                if args['promo'] is not None:
                    qry.promo = args['promo']
                if args['harga_promo'] is not None:
                    qry.harga_promo = args['harga_promo']
                if args['show'] is not None:
                    qry.show = args['show']
                if args['photo_url'] is not None:
                    qry.photo_url = args['photo_url']
                qry.updated_at = datetime.datetime.now()
                db.session.commit()
                return {'status': 'oke', 'items': marshal(qry, Items.response_fields)}, 200, {'Content-Type': 'application/json'}
            else:
                return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}

    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] == 'seller' or jwtClaims['status'] == 'admin':
            qry = Items.query.get(id)
            if qry is not None:
                if jwtClaims['status'] == 'seller':
                    if qry.id_penjual != jwtClaims['client_id']:
                        return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
                db.session.delete(qry)
                db.session.commit()
                return 'deleted', 200, {'Content-Type': 'application/json'}
            else:
                return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        print(jwtClaims['status'])
        if jwtClaims['status'] == 'seller' or jwtClaims['status'] == 'admin':
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
            parser.add_argument('photo_url', location='json')
            args = parser.parse_args()
            if args['promo'] is None:
                args['harga_promo'] = args['harga']
            if args['status'] == 'pre-order':
                args['stok'] = -1
            args['id_penjual'] = jwtClaims['client_id']
            seller_kota = Seller.query.filter(Seller.client_id == args['id_penjual']).first().kota
            seller_name = Seller.query.filter(Seller.client_id == args['id_penjual']).first().name
            args['id_kategori'] = Category.query.filter(Category.nama_kategori == args['kategori']).first().id
            args['created_at'] = datetime.datetime.now()
            args['updated_at'] = datetime.datetime.now()
            items = Items(None, args['id_penjual'], args['id_kategori'], args['nama'], args['merk'], args['harga'], args['status'], args['stok'], args['deskripsi_produk'], args['berat'], args['promo'], args['harga_promo'], args['show'], seller_name, seller_kota, args['photo_url'], args['created_at'], args['updated_at'])
            db.session.add(items)
            db.session.commit()
            return {'status': 'oke', 'items': marshal(items, Items.response_fields)}, 200, {'Content-Type': 'application/json'}
        else:
            return {'status': 'UNAUTHORIZED', 'message': 'Not Authorized'}, 401, {'Content-Type': 'application/json'}
    
    def options(self, id=None):
        return {'status': 'oke'}, 200

api.add_resource(ItemsResource, '/<int:id>', '')