from blueprints import db
from flask_restful import fields
from sqlalchemy.orm import backref
from blueprints.location import *
from blueprints.client import *
import datetime

class Seller(db.Model):
    __tablename__ = "seller"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    phone_number = db.Column(db.String(13), nullable=False)
    alamat = db.Column(db.String(100), nullable=False)
    provinsi = db.Column(db.String(30), nullable=False)
    kota = db.Column(db.String(30), nullable=False)
    id_kota = db.Column(db.Integer, nullable=False)
    bank = db.Column(db.String(10), nullable=False)
    no_rekening = db.Column(db.String(15), nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    
    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'date_of_birth': fields.DateTime,
        'gender': fields.String,
        'phone_number': fields.String,
        'alamat': fields.String,
        'provinsi': fields.String,
        'kota': fields.String,
        'id_kota': fields.Integer,
        'bank': fields.String,
        'no_rekening': fields.String,
        'client_id': fields.Integer,
        'photo_url': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }
    def __init__(self, id, name, date_of_birth, gender, phone_number, alamat, provinsi, kota, id_kota, bank, no_rekening, client_id, photo_url, created_at, updated_at):
        self.id = id
        self.name = name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone_number = phone_number
        self.alamat = alamat
        self.provinsi = provinsi
        self.kota = kota
        self.id_kota = id_kota
        self.bank = bank
        self.no_rekening = no_rekening
        self.client_id = client_id
        self.photo_url = photo_url
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return str(self.client_id)  # harus string