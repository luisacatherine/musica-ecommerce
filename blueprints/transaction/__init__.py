from blueprints import db
from flask_restful import fields
from blueprints.items import *
from blueprints.user import *
from blueprints.location import *
from blueprints.transaction_details import *
import datetime

class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    payment_method = db.Column(db.String(10))
    user_id = db.Column(db.Integer)
    seller_id = db.Column(db.Integer)
    alamat = db.Column(db.String(100), nullable=False)
    kota = db.Column(db.String(30), nullable=False)
    id_kota = db.Column(db.Integer, nullable=False)
    total_item = db.Column(db.Integer)
    total_berat = db.Column(db.Integer)
    total_ongkir = db.Column(db.Integer)
    total_harga = db.Column(db.Integer)
    status_transaksi = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    
    response_fields = {
        'id': fields.Integer,
        'payment_method': fields.String,
        'user_id': fields.Integer,
        'seller_id': fields.Integer,
        'alamat': fields.String,
        'kota': fields.String,
        'id_kota': fields.Integer,
        'total_item': fields.Integer,
        'total_berat': fields.Integer,
        'total_ongkir': fields.Integer,
        'total_harga': fields.Integer,
        'status_transaksi': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, id, payment_method, user_id, seller_id, alamat, kota, id_kota, total_item, total_berat, total_ongkir, total_harga, status_transaksi, created_at, updated_at):
        self.id = id
        self.payment_method = payment_method
        self.user_id = user_id
        self.seller_id = seller_id
        self.alamat = alamat
        self.kota = kota
        self.id_kota = id_kota
        self.total_item = total_item
        self.total_berat = total_berat
        self.total_ongkir = total_ongkir
        self.total_harga = total_harga
        self.status_transaksi = status_transaksi
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Transaction %r>' % self.id  # harus string