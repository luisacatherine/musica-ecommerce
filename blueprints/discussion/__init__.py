from blueprints import db
from flask_restful import fields
import datetime
from blueprints.seller import *
from blueprints.items import *

class Discussion(db.Model):
    __tablename__ = "Discussion"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_produk = db.Column(db.Integer, nullable=False)
    id_pembeli = db.Column(db.Integer, nullable=False)
    isi_diskusi = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)

    response_fields = {
        'id': fields.Integer,
        'id_produk': fields.Integer,
        'id_pembeli': fields.Integer,
        'isi_diskusi': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, id, id_produk, id_pembeli, isi_diskusi, created_at, updated_at):
        self.id = id
        self.id_produk = id_produk
        self.id_pembeli = id_pembeli
        self.isi_diskusi = isi_diskusi
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Discussion %r>' % self.id # harus string
