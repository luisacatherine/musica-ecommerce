import logging
import random
from blueprints import db
from flask_restful import fields
# from blueprints.user import *
import datetime


class Client(db.Model):
    __tablename__ = "client"
    client_id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)

    response_fields = {
        'client_id': fields.Integer,
        'email': fields.String,
        'password': fields.String,
        'status': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime
    }

    def __init__(self, client_id, email, password, status, created_at, updated_at):
        self.client_id = client_id
        self.email = email
        self.password = password
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Client %r>' % self.client_id  # harus string
