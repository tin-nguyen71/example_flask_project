import os
import datetime
import re
from flask import Blueprint, jsonify, request, current_app as capp
from voluptuous import Schema, Required, All
from google.oauth2 import id_token
from google.auth.transport import requests

from models.user import User
from system.authentication_jwt import encode_access_token
from system.schema_validator import validated, DateSchema, EmailSchema
from system.exceptions import NotFound

bp = Blueprint("user", __name__, url_prefix="/users")

LoginSchema = Schema({
    Required("token_id"): str,
    Required("login_type"): str
})

@bp.route("/login", methods=["POST"])
@validated(LoginSchema)
def login():
    if request.data["login_type"] == "google":
        try:
            user_info = id_token.verify_oauth2_token(request.data["token_id"], requests.Request(), "450396104591-mlij4rd7ul0lj6s2gt200bpnab88i2h2.apps.googleusercontent.com")
            user = capp.sess.query(User).filter_by(username=user_info["email"]).first()
            if not user:
                user_object = {
                    'username': user_info["email"],
                    'name': user_info["name"],
                    'picture': user_info["picture"]
                }
                user = User(**user_object)
                capp.sess.add(user)
                capp.sess.commit()
        except ValueError:
            return jsonify({"login": "token expired"}), 401
    return jsonify({"user": user.to_json(), "token": encode_access_token(user.client_id)})


UserRegisterSchema = Schema({
    Required("mountpoint"): str,
    Required("username"): str,
    Required("password"): str,
    Required("address"): str,
    Required("publish_acl"): str,
    Required("subscribe_acl"): str,
})

@bp.route("/register", methods=["POST"])
@validated(UserRegisterSchema)
def register():
    data = request.data
    user = User(**{
        'mountpoint': data["mountpoint"],
        'username': data["username"],
        'password': data["password"],
        'address': data["address"],
        'publish_acl': data["publish_acl"],
        'subscribe_acl': data["subscribe_acl"],
    })
    capp.sess.add(user)
    capp.sess.commit()
    return jsonify({"user": user.to_json(), "token": encode_access_token(user.client_id)})

# LoginSchemaTemp = Schema({
#     Required("email"): str
# })

# @bp.route("/login_temp", methods=["POST"])
# @validated(LoginSchemaTemp)
# def login_temp():
#     user = capp.sess.query(User).filter_by(username=request.data["email"]).first()
#     return jsonify({"user": user
