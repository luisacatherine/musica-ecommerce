from flask import Flask, request
import json, logging
from time import strftime
from flask_restful import Resource, Api, reqparse, abort
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://musica:Alta2019#@musica.cbdr6ksottly.ap-southeast-1.rds.amazonaws.com:3306'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://alterra:Alta2019#@172.31.21.6:3306/dbmusica'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@0.0.0.0:3306/musica_project'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'musicaAdmin'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# catch 404 default error
api = Api(app, catch_all_404s=True)

# middlewares
@app.after_request
def after_request(response):
    if request.method == 'GET':
        app.logger.warning("REQUEST LOG\t%s %s", json.dumps({'request': request.args.to_dict(
        ), 'response': json.loads(response.data.decode('utf-8'))}), response.status_code)
    else:
        app.logger.warning("REQUEST LOG\t%s %s", json.dumps({'request': request.get_json(
        ), 'response': json.loads(response.data.decode('utf-8'))}), response.status_code)
    return response

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity

# call blueprints
from blueprints.client.resources import bp_client
from blueprints.user.resources import bp_user
from blueprints.auth import bp_auth
from blueprints.seller.resources import bp_seller
from blueprints.items.resources import bp_item
from blueprints.transaction_details.resources import bp_transdetail
from blueprints.transaction.resources import bp_transaction
from blueprints.discussion.resources import bp_diskusi
from blueprints.category.resources import bp_category
from blueprints.ongkir import bp_ongkir
from blueprints.seller.public import bp_seller_public
from blueprints.user.public import bp_user_public
from blueprints.location.resources import bp_provinsi, bp_kota
from blueprints.status.resources import bp_status


app.register_blueprint(bp_client, url_prefix='/client')
app.register_blueprint(bp_user, url_prefix='/user')
app.register_blueprint(bp_auth, url_prefix='/login')
app.register_blueprint(bp_seller, url_prefix='/seller')
app.register_blueprint(bp_item, url_prefix='/item')
app.register_blueprint(bp_transdetail, url_prefix='/transdetail')
app.register_blueprint(bp_transaction, url_prefix='/transaction')
app.register_blueprint(bp_diskusi, url_prefix='/diskusi')
app.register_blueprint(bp_category, url_prefix='/category')
app.register_blueprint(bp_ongkir, url_prefix='/ongkir')
app.register_blueprint(bp_seller_public, url_prefix='/public/seller')
app.register_blueprint(bp_user_public, url_prefix='/public/user')
app.register_blueprint(bp_provinsi, url_prefix='/provinsi')
app.register_blueprint(bp_kota, url_prefix='/kota')
app.register_blueprint(bp_status, url_prefix='/status')

db.create_all()
