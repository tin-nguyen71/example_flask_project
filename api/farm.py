import datetime
import json
import uuid

from flask import Blueprint
from flask import current_app as capp
from flask import jsonify, request
from flasgger import swag_from
from voluptuous import Required, Schema, Optional, ALLOW_EXTRA

from system.authentication_jwt import authorized, authentication, authorized_farm
from system.schema_validator import validated
from system.exceptions import BadRequest, UserInputInvalid
from models.farm import Farm
from models.user import User
from models.user_farm import UserFarm
from models.user_pond import UserPond
from models.user_device import UserDevice
from system.datetime_util import get_now

bp = Blueprint("farm", __name__, url_prefix="/farms")

CreateFarmSchema = Schema({
    Required("name"): str,
    Required("secret"): str,
    Optional("address"): str
})

@bp.route("/", methods=["POST"])
# @authorized()
@validated(CreateFarmSchema)
def create():
    request.data["updated_action"] = "create"
    farm = Farm(**request.data)
    capp.sess.add(farm)
    subscribe_acl = "[{'pattern':'/farm/" + str(farm.id) + "'}]"
    client_id = str(farm.id).replace("farm","user")
    user = User(**{
        'client_id': client_id,
        'mountpoint': "",
        'username': farm.name,
        'password': farm.secret,
        'address': farm.address,
        'publish_acl': "[{'pattern':'/worker/+'}]",
        'subscribe_acl': subscribe_acl,
        'updated_action': 'create'
    })
    capp.sess.add(user)
    capp.sess.commit()
    return jsonify(farm.to_json()), 201

UserAddFarm = Schema({
    Required("farm_id"): str,
    Required("secret"): str
})

@bp.route("/add_farm", methods=["POST"])
@authorized()
@validated(UserAddFarm)
def user_add_farm():
    farm = capp.sess.query(Farm).filter_by(id=request.data["farm_id"]).first()
    if not farm:
        return jsonify({"farm": "Not Found"}), 404
    if not farm.check_secret(request.data["secret"]):
        return jsonify({"detail": "Wrong secret"}), 400
    user_farm = {
        "farm_id": farm.id,
        "client_id": request.user_id,
        "role_admin": True,
        "role_update": True,
        "role_view": True,
    }
    user_farm_db = UserFarm(**user_farm)
    capp.sess.add(user_farm_db)
    capp.sess.commit()
    return jsonify(farm.to_json())


@bp.route("/<string:id>", methods=["GET"])
@authorized()
def get_by_farm_id(id):
    farm = capp.sess.query(Farm).filter_by(id=id).first()
    if not farm:
        return jsonify({"farm": "Not Found"}), 404
    rv = farm.to_json()
    rv["ponds"] = []
    for i in farm.pond:
        rv["ponds"].append(i.to_json())
    return jsonify(rv)


@bp.route("/", methods=["GET"])
@authorized()
def get_by_user_id():
    return jsonify({"status": True, "deatail": [i.to_json() for i in request.user.farm]})

AdminAddUserFarm = Schema({
    Required("farm_id"): str
}, extra=ALLOW_EXTRA)

@bp.route("/add_user", methods=["POST"])
@validated(AdminAddUserFarm)
@authentication()
# @authorized_farm("role_admin")
def admin_farm_add_user():
    farm = capp.sess.query(Farm).filter_by(id=request.data["farm_id"]).first()
    if not farm:
        return jsonify({"farm": "Not Found"}), 404
    user_farm = capp.sess.query(UserFarm).filter_by(farm_id=request.data["farm_id"], client_id=request.user_id).first()

    if not user_farm:
        return jsonify({"user_farm": "Not Found"}), 404

    if not user_farm.role_admin:
        return jsonify({"detail": "permission deny"}), 403

    for user_id in request.data["user_ids"]:
        user_add = capp.sess.query(User).filter_by(client_id=user_id).first()
        if user_add:
            user_farm_add = {
                "farm_id": farm.id,
                "client_id": user_id,
                "role_admin": False,
                "role_update": False,
                "role_view": True
            }
            # create user_farm object
            user_farm_add_db = UserFarm(**user_farm_add)
            capp.sess.add(user_farm_add_db)

            # create user_pond and user_device object
            for pond in farm.pond:
                user_pond_add = {
                    "pond_id": pond.id,
                    "client_id": user_id,
                    "role_admin": False,
                    "role_update": False,
                    "role_view": True        
                }
                user_pond_db = UserPond(**user_pond_add)
                capp.sess.add(user_pond_db)

                for device in pond.device:
                    user_device_add = {
                        "device_id": device.id,
                        "client_id": user_id,
                        "role_admin": False,
                        "role_update": False,
                        "role_view": True
                    }
                    user_device_db = UserDevice(**user_device_add)
                    capp.sess.add(user_device_db)

    capp.sess.commit()
    return jsonify(farm.to_json())
