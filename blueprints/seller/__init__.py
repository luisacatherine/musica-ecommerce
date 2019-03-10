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
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    alamat = db.Column(db.String(100), nullable=False)
    kota = db.Column(db.String(30), nullable=False)
    id_kota = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship("Client", backref=backref("seller", uselist=False))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    
    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'age': fields.Integer,
        'gender': fields.String,
        'alamat': fields.String,
        'kota': fields.String,
        'id_kota': fields.Integer,
        'client_id': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, id, name, age, gender, alamat, kota, id_kota, client_id, created_at, updated_at):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.alamat = alamat
        self.kota = kota
        self.id_kota = id_kota
        self.client_id = client_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Seller %r>' % self.id  # harus string