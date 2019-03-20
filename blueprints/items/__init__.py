from blueprints import db
from flask_restful import fields
import datetime
from blueprints.seller import *
from blueprints.category import *

class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_penjual = db.Column(db.Integer, nullable=False)
    id_kategori = db.Column(db.Integer, nullable=False)
    nama = db.Column(db.String(50), nullable=False)
    merk = db.Column(db.String(50), nullable=True)
    harga = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    deskripsi_produk = db.Column(db.String(1000))
    berat = db.Column(db.Integer, nullable=False)
    promo = db.Column(db.Boolean, nullable=False, default=False)
    harga_promo = db.Column(db.Integer, nullable=True)
    show = db.Column(db.Boolean, nullable=False, default=True)
    seller = db.Column(db.String(50), nullable=False)
    seller_city = db.Column(db.String(50), nullable=False)
    photo_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)

    response_fields = {
        'id': fields.Integer,
        'id_penjual': fields.Integer,
        'id_kategori': fields.Integer,
        'nama': fields.String,
        'merk': fields.String,
        'harga': fields.Integer,
        'status': fields.String,
        'stok': fields.Integer,
        'deskripsi_produk': fields.String,
        'berat': fields.Integer,
        'promo': fields.Boolean,
        'harga_promo': fields.Integer,
        'show': fields.Boolean,
        'seller': fields.String,
        'seller_city': fields.String,
        'photo_url' : fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, id, id_penjual, id_kategori, nama, merk, harga, status, stok, deskripsi_produk, berat, promo, harga_promo, show, seller, seller_city, photo_url, created_at, updated_at):
        self.id = id
        self.id_penjual = id_penjual
        self.id_kategori = id_kategori
        self.nama = nama
        self.merk = merk
        self.harga = harga
        self.status = status
        self.stok = stok
        self.deskripsi_produk = deskripsi_produk
        self.berat = berat
        self.promo = promo
        self.harga_promo = harga_promo
        self.show = show
        self.seller = seller
        self.seller_city = seller_city
        self.photo_url = photo_url
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Items %r>' % self.id # harus string