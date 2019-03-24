import logging
import json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from . import *
from flask_jwt_extended import get_jwt_claims, jwt_required
import datetime

bp_diskusi = Blueprint('diskusi', __name__)
api = Api(bp_diskusi)

class DiscussionResource(Resource):

    def __init__(self):
        pass
    
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id_produk', location='args', required=True, type=int)
        parser.add_argument('p', location='args', type=int)
        parser.add_argument('rp', location='args', type=int)
        args = parser.parse_args()
        qry = Items.query.get(args['id_produk'])
        if qry is None:
            return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
        qry = Discussion.query
        rows = []
        if (args['p'] is not None and args['rp'] is not None):
            offset = (args['p'] * args['rp']) - args['rp']            
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Discussion.response_fields))
            return {'status': 'oke', 'diskusi': rows}, 200, {'Content-Type': 'application/json'}
        else:
            for row in qry.all():
                rows.append(marshal(qry, Discussion.response_fields))
            return {'status': 'oke', 'diskusi': rows}, 200, {'Content-Type': 'application/json'}
    
    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('id_produk', location='json', required=True, type=int)
        parser.add_argument('isi_diskusi', location='json', required=True)
        args = parser.parse_args()
        qry = Items.query.get(args['id_produk'])
        if qry is None:
            return {'status': 'NOT_FOUND', 'message': 'Items not found'}, 404, {'Content-Type': 'application/json'}
        id_pembeli = jwtClaims['client_id']
        args['created_at'] = datetime.datetime.now()
        args['updated_at'] = datetime.datetime.now()
        discussion = Discussion(None, args['id_produk'], id_pembeli, args['isi_diskusi'], args['created_at'], args['updated_at'])
        db.session.add(discussion)
        db.session.commit()
        return marshal(discussion, Discussion.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(DiscussionResource, '/<int:id>', '')