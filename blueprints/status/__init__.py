from blueprints import db
from flask_restful import fields
import datetime
from blueprints.seller import *
from blueprints.items import *

class StatusTransaksi(db.Model):
    __tablename__ = "statustransaksi"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    status = db.Column(db.String(100), nullable=False)

    response_fields = {
        'id': fields.Integer,
        'status': fields.String
    }

    def __init__(self, id, status):
        self.id = id
        self.status = status

    def __repr__(self):
        return '<StatusTransaksi %r>' % self.id # harus string
