import logging
import random
from blueprints import db
from flask_restful import fields
from sqlalchemy.orm import backref

class Provinsi(db.Model):
    __tablename__ = "data_provinsi"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    nama_provinsi = db.Column(db.String(30))

    response_fields = {
        'id': fields.Integer,
        'nama_provinsi': fields.String
    }

    def __init__(self, id, nama_provinsi):
        self.id = id
        self.nama_provinsi = nama_provinsi

    def __repr__(self):
        return self.nama_provinsi  # harus string

class Kota(db.Model):
    __tablename__ = "data_kota"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    nama_provinsi = db.Column(db.String(30))
    nama_kota = db.Column(db.String(50))

    response_fields = {
        'id': fields.Integer,
        'nama_provinsi': fields.String,
        'nama_kota': fields.String
    }

    def __init__(self, id, nama_provinsi, nama_kota):
        self.id = id
        self.nama_provinsi = nama_provinsi
        self.nama_kota = nama_kota

    def __repr__(self):
        return self.nama_kota  # harus string