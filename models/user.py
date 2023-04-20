import datetime
import os
from unicodedata import name
import uuid
import hashlib

from sqlalchemy import Boolean, Column, DateTime, String, JSON, Integer
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from system.database_uuid import UUID
from util.common_validator import email_validator
from system.model_base import Base
from models.user_farm import UserFarm


class User(Base):
    __tablename__ = "vmq_auth_acl"
    __json_hidden__ = ["_password", "password", "_email", "_phone"]

    client_id = Column(String, primary_key=True, default="user-"+str(uuid.uuid4()).replace("-",""))
    mountpoint = Column(String, nullable=False, default="")
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, default="iotoom")
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    publish_acl = Column(String, nullable=True)
    subscribe_acl = Column(String, nullable=True)
    farm = relationship('Farm', secondary=UserFarm.__table__, backref='Item')
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    # @hybrid_property
    # def password(self):
    #     return self.password

    # @password.setter
    # def password(self, plain_password):
    #     self.password = hashlib.md5(plain_password.encode('utf8')).hexdigest()
            
    # validate phone

    def __init__(self, **kwargs):
        self.client_id = "user-"+str(uuid.uuid4()).replace("-","")
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f"<User id={self.id} email={self._email}>"

    def __str__(self):
        return self.__repr__()


    def check_password(self, password):
        pass_hash = hashlib.md5(password.encode('utf8')).hexdigest()
        if self.password == pass_hash:
            return True
        return False

    def to_json(self):
        rv = {
            "client_id": self.client_id,
            "username": self.username,
            "name": self.name,
            "picture": self.picture,
            "publish_acl": self.publish_acl,
            "subscribe_acl": self.subscribe_acl
        }
        return rv
