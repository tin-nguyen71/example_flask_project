import datetime
import uuid
from flask import request
from functools import wraps
from dateutil.parser import parse

from system.exceptions import UserInputInvalid, ApplicationError
from util.common_validator import email_validator
from system.datetime_util import get_now

valid_status = ["active", "blocked"]
valid_roles = ["writer", "editor", "manager", "none"]
payout_status = ["paid", "unpaid"]
# Measure water index: MWI, SE: save electric
valid_device_type = ["SE", "RFS", "MWI"]

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def EasyDateTimeValue(value):
    try:
        return parse(value)
    except ValueError:
        raise UserInputInvalid(f"'{value}' is an invalid format datetime")


def BooleanValue(value):
    if value is not None:
        value = value == 'true'
    return value


def EnumValue(enum_class):
    def validate_type(value):
        enum_list = enum_class.list()
        if value not in enum_list:
            raise UserInputInvalid(f"Invalid type '{value}', must be in {enum_list}")
        return value
    return validate_type


def UUIDSchema(value):
    return uuid.UUID(value)


def DateSchema(value):
    try:
        return datetime.datetime.strptime(value, DATE_FORMAT)
    except TypeError:
        raise UserInputInvalid(f"'{value}' must respect datetime format '{DATE_FORMAT}'")


def DateTimeSchema(value):
    try:
        if type(value) == datetime.datetime:
            return value
        return datetime.datetime.strptime(value, DATETIME_FORMAT)
    except TypeError:
        raise UserInputInvalid(f"'{value}' must respect datetime format '{DATETIME_FORMAT}'")

def EndDateSchema(value):
    try:
        if type(value) == datetime.datetime:
            return value
        value = datetime.datetime.strptime(value, DATETIME_FORMAT)
        if value < get_now():
            raise UserInputInvalid("end_date update must greater than now")
        return value
    except TypeError:
        raise UserInputInvalid(f"'{value}' must respect datetime format '{DATETIME_FORMAT}'")

def EditDateSchema(value):
    try:
        if type(value) == datetime.datetime:
            return value
        value = datetime.datetime.strptime(value, DATETIME_FORMAT)
        if value < get_now():
            raise UserInputInvalid("Date update must greater than now")
        return value
    except TypeError:
        raise UserInputInvalid(f"'{value}' must respect datetime format '{DATETIME_FORMAT}'")

def StatusSchema(value):
    if value not in valid_status:
        raise UserInputInvalid(f"Invalid Status : {value}")
    return value

def RoleSchema(value):
    if value not in valid_roles:
        raise UserInputInvalid(f"Invalid Role : {value}")
    return value

def EmailSchema(value):
    if email_validator(value) is False:
        raise UserInputInvalid(f"{value} is wrong email format")
    return value

def StatusPayoutSchema(value):
    if value not in payout_status:
        raise UserInputInvalid(f"Invalid status : {value}")
    return value 

def DeviceType(value):
    if value not in valid_device_type:
        raise UserInputInvalid("Invalid Device type:", value)
    return value


def validated(schema_validator):
    """
    Using to validate schema of request.data. Raise Voluptuous.Invalid if failed.
    """

    def internal(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not request.is_json:
                raise ApplicationError("Bad Request", detail="Expect json type body")
            data = schema_validator(request.get_json())
            request.data = data
            return func(*args, **kwargs)
        return decorated
    return internal
