import datetime
import json
import uuid

from flask import Blueprint
from flask import current_app as capp
from flask import jsonify, request
from flasgger import swag_from
from voluptuous import Required, Schema, Optional, ALLOW_EXTRA
from models.user_device import UserDevice

from system.authentication_jwt import authorized, authentication, authorized_pond
from system.schema_validator import validated
from system.exceptions import BadRequest, UserInputInvalid
from models.farm import Farm
from models.user import User
from models.pond import Pond
from models.device import Device
from models.user_farm import UserFarm
from models.user_pond import UserPond

bp = Blueprint("pond", __name__, url_prefix="/ponds")

CreateFarmSchema = Schema({
    Required("name"): str,
    Required("farm_id"): str
})

@bp.route("/", methods=["POST"])
@authentication()
@validated(CreateFarmSchema)
@authorized_pond("role_admin")
def create():
    pond = Pond(**request.data)
    capp.sess.add(pond)
    capp.sess.commit()

    # Add user_pond for anorther person in their team
    # Get list userID and create user_pond
    user_farms = capp.sess.query(UserFarm).filter_by(farm_id=request.data["farm_id"])
    if user_farms:
        for user_farm in user_farms:
            if user_farm.client_id == request.user_id:
                user_pond = {
                    "pond_id": pond.id,
                    "client_id": user_farm.client_id,
                    "role_admin": True,
                    "role_update": True,
                    "role_view": True        
                }
            else:
                user_pond = {
                    "pond_id": pond.id,
                    "client_id": user_farm.client_id,
                    "role_admin": False,
                    "role_update": False,
                    "role_view": True        
                }
            user_pond_db = UserPond(**user_pond)
            capp.sess.add(user_pond_db)
        capp.sess.commit()
    
    return jsonify(pond.to_json()), 201

AddUserToPond = Schema({
    Required("farm_id"): str
}, extra=ALLOW_EXTRA)

@bp.route("/<string:id>/grant_permission", methods=["POST"])
@authentication()
@validated(AddUserToPond)
@authorized_pond("role_admin")
def updated_user_pond_role(id):
    pond = capp.sess.query(Pond).filter_by(id=id).first()
    if not pond:
        return jsonify({"pond": "Not Found"}), 404

    devices = capp.sess.query(Device).filter_by(pond_id=id)
    
    # update both user_pond and user_device
    for user_pond in request.data["user_ponds"]:
        user_pond_temp = capp.sess.query(UserPond).filter_by(pond_id=id, client_id=user_pond["client_id"]).first()
        if user_pond_temp.role_admin == False:
            if user_pond_temp:
                user_pond_temp.role_update = user_pond["role_update"]
                capp.sess.add(user_pond_temp)
            if devices:
                for device in devices:
                    user_device_temp = capp.sess.query(UserDevice).filter_by(device_id=device.id, client_id=user_pond["client_id"]).first()
                    user_device_temp.role_update = user_pond["role_update"]
                    capp.sess.add(user_device_temp)
    capp.sess.commit()
    return jsonify(pond.to_json())

# write api for get all pond 
# get pond by id
# get all device by pond id
# get device by id
@bp.route("/", methods=["GET"])
@authorized()
def get_all_pond_by_user_id():
    user_ponds = capp.sess.query(UserPond).filter_by(client_id=request.user_id)
    if not user_ponds:
        return jsonify({"pond": "Not Found"}), 404 
    result = []
    for user_pond in user_ponds:
        result.append({
            "pond": user_pond.pond.to_json(),
            "user_pond": user_pond.to_json()
        })
    return jsonify({
        "status": True, 
        "result": result
        })

@bp.route("/<string:id>", methods=["GET"])
@authorized()
def get_pond_by_pond_id(id):
    user_pond = capp.sess.query(UserPond).filter_by(client_id=request.user_id, pond_id=id).first()
    if not user_pond:
        return jsonify({"pond": "Not Found"}), 404 
    return jsonify({
        "status": True, 
        "result": {
        "pond": user_pond.pond.to_json(),
        "user_pond": user_pond.to_json()
        }})
