import logging
import random
from blueprints import db
from flask_restful import fields


class Client(db.Model):
    __tablename__ = "client"
    client_id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    client_key = db.Column(db.String(50), unique=True, nullable=False)
    client_secret = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False)

    response_fields = {
        'client_id': fields.Integer,
        'client_key': fields.String,
        'client_secret': fields.String,
        'status': fields.Integer
    }

    def __init__(self, client_id, client_key, client_secret, status):
        self.client_id = client_id
        self.client_key = client_key
        self.client_secret = client_secret
        self.status = status

    def __repr__(self):
        return '<Client %r>' % self.client_id  # harus string
