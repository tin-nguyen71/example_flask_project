import os
from functools import wraps
import datetime
import jwt
from flask import jsonify, request, current_app as capp
from functional import seq

from system.exceptions import ApplicationError, make_error, PermissionDenied, SystemException

from models.user import User
from models.user_farm import UserFarm
# from models.model_enum import StaffType

# permitted_staff_roles = [StaffType.writer.value, StaffType.editor.value, StaffType.manager.value]

# def must_be(staff_role_array=None):
#     def check_staff_role(fn):
#         @wraps(fn)
#         def internal(*args, **kwargs):
#             if not hasattr(request, 'user_id'):
#                 raise SystemException("must_be decorator must placed below authorized decorator")

#             staff = Staff.query.get_or_404(request.user_id)
#             if staff_role_array:
#                 if set(staff_role_array).issubset(permitted_staff_roles) is False:
#                     raise AssertionError(f"An API have a strange role {staff_role_array}")

#             if staff.role not in staff_role_array:
#                 raise PermissionDenied(f"You're not {str(staff_role_array)}") 

#             return fn(*args, **kwargs)
#         return internal
#     return check_staff_role

def authorized(role_string=None):
    def real_jwt_required(fn):
        @wraps(fn)
        def internal(*args, **kwargs):
            # If this API have role_strings, add to permitted_roles for checking later
            try:
                token = request.headers["Authorization"].split(" ")
                if len(token) != 2 or token[0] != "JWT":
                    raise jwt.InvalidTokenError
                payload = jwt.decode(token[1], "18011001", algorithms=["HS256"])
                
            except KeyError:
                return jsonify(
                    {"success": False, "message": "Authorization Header must be provide."}
                ), 401
            except jwt.ExpiredSignatureError:
                return jsonify(
                    {"success": False, "message": "Signature expired. Please log in again."}
                ), 401
            except jwt.InvalidTokenError:
                return jsonify(
                    {"success": False, "message": "Invalid token. Please check your token carefully or login again."}
                ), 401
            except ApplicationError as app_err:
                return make_error(app_err.message, detail=app_err.detail, code=403)

            user = capp.sess.query(User).filter_by(client_id=payload["id"]).first()
            if not user:
                return jsonify({"status": False}), 404
            request.user = user
            request.user_id = payload["id"]
            return fn(*args, **kwargs)
        return internal
    return real_jwt_required

def authentication():
    def real_jwt_required(fn):
        @wraps(fn)
        def internal(*args, **kwargs):
            # If this API have role_strings, add to permitted_roles for checking later
            try:
                token = request.headers["Authorization"].split(" ")
                if len(token) != 2 or token[0] != "JWT":
                    raise jwt.InvalidTokenError
                payload = jwt.decode(token[1], "18011001", algorithms=["HS256"])
                
            except KeyError:
                return jsonify(
                    {"success": False, "message": "Authorization Header must be provide."}
                ), 401
            except jwt.ExpiredSignatureError:
                return jsonify(
                    {"success": False, "message": "Signature expired. Please log in again."}
                ), 401
            except jwt.InvalidTokenError:
                return jsonify(
                    {"success": False, "message": "Invalid token. Please check your token carefully or login again."}
                ), 401
            except ApplicationError as app_err:
                return make_error(app_err.message, detail=app_err.detail, code=403)

            user = capp.sess.query(User).filter_by(client_id=payload["id"]).first()
            if not user:
                return jsonify({"status": False}), 404
            request.user = user
            request.user_id = payload["id"]
            return fn(*args, **kwargs)
        return internal
    return real_jwt_required


def authorized_pond(role_string=None):
    def real_jwt_required(fn):
        @wraps(fn)
        def internal(*args, **kwargs):
            # If this API have role_strings, add to permitted_roles for checking later
            if not role_string:
                return False
            if role_string == "role_admin":
                user_farm = capp.sess.query(UserFarm).filter_by(client_id=request.user_id, farm_id=request.data["farm_id"]).first()
                if not user_farm or user_farm.role_admin == False:
                    return jsonify({"status": False, "detail": "AUthor faild"}), 401
            request.farm_id = request.data["farm_id"]
            return fn(*args, **kwargs)
        return internal
    return real_jwt_required

def authorized_farm(role_string=None):
    def real_jwt_required(fn):
        @wraps(fn)
        def internal(*args, **kwargs):
            # If this API have role_strings, add to permitted_roles for checking later
            if not role_string:
                return False
            if role_string == "role_admin":
                user_farm = capp.sess.query(UserFarm).filter_by(client_id=request.user_id, farm_id=request.data["farm_id"]).first()
                if not user_farm or user_farm.role_admin == False:
                    return jsonify({"status": False, "detail": "AUthor faild"}), 401
            request.farm_id = request.data["farm_id"]
            return fn(*args, **kwargs)
        return internal
    return real_jwt_required

def encode_access_token(user_id) -> str:
    """
    Warn: user_id can be UUID so it need str(user_id)
    """
    # if role not in ["staff", "user", "guest"]:
    #     raise ApplicationError("Role is not valid.")
    payload = {
        "id": str(user_id),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, "18011001", algorithm="HS256")
