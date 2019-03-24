import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints.location import *
import requests

bp_ongkir = Blueprint('ongkir', __name__)
api = Api(bp_ongkir)

class OngkirResources(Resource):

    def get(self):
        data_kota = str(Kota.query.all())
        parser = reqparse.RequestParser()
        parser.add_argument('origin', location='args', choices=data_kota, required=True)
        parser.add_argument('destination', location='args', choices=data_kota, required=True)
        parser.add_argument('weight', location='args')
        args = parser.parse_args()
        origin = Kota.query.filter(Kota.nama_kota == args['origin']).first().id
        destination = Kota.query.filter(Kota.nama_kota == args['destination']).first().id
        host = 'http://api.rajaongkir.com/starter'
        headers = {'key': 'fe20e3f08b529d49f43143180513be36'}
        rq = requests.post(host + '/cost', headers = headers, data={'origin': origin, 'destination': destination, 'weight': args['weight'], 'courier': 'jne'})
        hasil = rq.json()
        return {'status': 'oke', 'ongkir': hasil['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']}, 200

    def options(self):
        return {},200

api.add_resource(OngkirResources, '')