"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, current_app
from api.models import db, User, Task
from api.utils import generate_sitemap, APIException

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

import bcrypt

import cloudinary
import cloudinary.uploader
import cloudinary.api

from flask_mail import Mail, Message

import datetime

api = Blueprint('api', __name__)

cloudinary.config(
    cloud_name = "dl1tsitgq",
    api_key = "147172381478392",
    api_secret = "4k9aIap6Pyd6KGtpFvqVgd-L7l8",
)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

#------------------------------------------------------
#------------------------------------------------------
#------------------------------------------------------
CODE_FORMAT = 'UTF-8'

@api.route("/hello-heroku", methods=["GET"])
def hello_heroku():
    return jsonify("hello heroku"), 200

@api.route('/signup', methods=['POST'])
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

@api.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException("Email doesn't exist", status_code=404)
    
    if not bcrypt.checkpw(bytes(password, CODE_FORMAT), bytes(user.password, CODE_FORMAT)):
        raise APIException("Password is incorrect", status_code=404)

    expires = datetime.timedelta(days=365)
    token = create_access_token(identity=user.id, expires_delta=expires)
    return jsonify(token)

@api.route('/task', methods=['POST'])
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
    
    
    mail = Mail(current_app)
    msg = Message("Hello",
                  sender="from@example.com",
                  recipients=["to@example.com"])
    msg.html = "<b>testing</b>"
    mail.send(msg)

    return jsonify(task.serialize()), 201