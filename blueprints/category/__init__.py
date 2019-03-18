from blueprints import db
from flask_restful import fields
import datetime

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    nama_kategori = db.Column(db.String(30))
    url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)

    response_fields = {
        'id': fields.Integer,
        'nama_kategori': fields.String,
        'url': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime

    }

    def __init__(self, id, nama_kategori, url, created_at, updated_at):
        self.id = id
        self.nama_kategori = nama_kategori
        self.url = url
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return self.nama_kategori  # harus string