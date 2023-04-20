import datetime
import json
import uuid

from flask import Blueprint
from flask import current_app as capp
from flask import jsonify, request
from flasgger import swag_from
from voluptuous import Required, Schema, Optional, ALLOW_EXTRA

from system.authentication_jwt import authorized, authentication, authorized_pond
from system.schema_validator import validated, DeviceType
from system.exceptions import BadRequest, UserInputInvalid
from models.farm import Farm
from models.user import User
from models.pond import Pond
from models.user_farm import UserFarm
from models.user_pond import UserPond
from models.device import Device
from models.user_device import UserDevice

bp = Blueprint("device", __name__, url_prefix="/devices")

CreateDeviceSchema = Schema({
    Required("name"): str,
    Required("pond_id"): str,
    Required("type"): DeviceType,
})

@bp.route("/", methods=["POST"])
@authentication()
@validated(CreateDeviceSchema)
def create():
    pond = capp.sess.query(Pond).filter_by(id=request.data["pond_id"]).first()
    if not pond:
        return jsonify({"pond": "Not Found"}), 404

    user_pond = capp.sess.query(UserPond).filter_by(client_id=request.user_id, pond_id=request.data["pond_id"], role_admin=True).first()
    if not user_pond:
        return jsonify({"Authorization": "FAILD"}), 403

    request.data["data"] = ""
    device = Device(**request.data)
    capp.sess.add(device)
    capp.sess.commit()

    # Create user_device for all user of their team
    user_ponds = capp.sess.query(UserPond).filter_by(pond_id=request.data["pond_id"])
    if user_ponds:
        for user_pond in user_ponds:
            user_device = {
                "device_id": device.id,
                "client_id": user_pond.client_id,
                "role_admin": user_pond.role_admin,
                "role_update": user_pond.role_update,
                "role_view": user_pond.role_view        
            }
            user_device_db = UserDevice(**user_device)
            capp.sess.add(user_device_db)
        capp.sess.commit()
    return jsonify(device.to_json()), 201


@bp.route("/", methods=["GET"])
@authorized()
def get_all_devices():
    user_devices = capp.sess.query(UserDevice).filter_by(client_id=request.user_id)
    if not user_devices:
        return jsonify({"pond": "Not Found"}), 404 
    result = []
    for user_device in user_devices:
        result.append({
            "device": user_device.device.to_json(),
            "user_device": user_device.to_json()
        })
    return jsonify({
        "status": True, 
        "result": result
        })

@bp.route("/<string:id>", methods=["GET"])
@authorized()
def get_device_by_device_id(id):
    user_device = capp.sess.query(UserDevice).filter_by(client_id=request.user_id, device_id=id).first()
    if not user_device:
        return jsonify({"pond": "Not Found"}), 404  
    return jsonify({
        "status": True, 
        "result": {
        "device": user_device.device.to_json(),
        "user_device": user_device.to_json()
        }})


# updat farm, pond, dv
# list usr by pond 