"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, User, Task
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import JWTManager

import bcrypt

import cloudinary
import cloudinary.uploader
import cloudinary.api



#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

cloudinary.config(
    cloud_name = "dl1tsitgq",
    api_key = "147172381478392",
    api_secret = "4k9aIap6Pyd6KGtpFvqVgd-L7l8",
)

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

#------------------------------------------------------
#------------------------------------------------------
#------------------------------------------------------
CODE_FORMAT = 'UTF-8'

@app.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    user = User.query.filter_by(email=email).first()
    if user:
        raise APIException("User exists")
    
    hashed = bcrypt.hashpw(bytes(password, CODE_FORMAT), bcrypt.gensalt())
    user = User(email=email, password=hashed.decode(CODE_FORMAT), is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException("Email doesn't exist", status_code=404)
    
    if not bcrypt.checkpw(bytes(password, CODE_FORMAT), bytes(user.password, CODE_FORMAT)):
        raise APIException("Password is incorrect", status_code=404)

    token = create_access_token(identity=user.id)
    return jsonify(token)

@app.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    body = request.form
    text = body["text"]
    image = request.files["image"]
    response = cloudinary.uploader.upload(image)
    user_id = get_jwt_identity()
    task = Task(text=text, user_id=user_id, url=response["url"])

    db.session.add(task)
    db.session.commit()
    return jsonify(task.serialize()), 201


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
