from blueprints import db
from flask_restful import fields
from blueprints.items import *
from blueprints.transaction import *
import datetime

class TransactionDetail(db.Model):
    __tablename__ = "transaction_detail"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    transaction_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    harga = db.Column(db.Integer, nullable = False)
    berat = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    
    response_fields = {
        'id': fields.Integer,
        'transaction_id': fields.Integer,
        'product_id': fields.Integer,
        'seller_id': fields.Integer,
        'buyer_id': fields.Integer,
        'qty': fields.Integer,
        'harga': fields.Integer,
        'berat': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, id, transaction_id, product_id, seller_id, buyer_id, qty, harga, berat, created_at, updated_at):
        self.id = id
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.qty = qty
        self.harga = harga
        self.berat = berat
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<TransactionDetail %r>' % self.id  # harus string