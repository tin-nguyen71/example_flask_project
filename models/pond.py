import datetime
import os
import uuid
import hashlib

from sqlalchemy import Boolean, Column, DateTime, String, JSON, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from system.database_uuid import UUID
from util.common_validator import email_validator

from system.model_base import Base


class Pond(Base):
    __tablename__ = "pond"

    id = Column(String, primary_key=True, default="pond-"+str(uuid.uuid4()).replace("-",""))
    farm_id = Column(String, ForeignKey("farm.id", ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)

    device = relationship("Device", lazy='select')

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    def __init__(self, **kwargs):
        self.id = "pond-"+str(uuid.uuid4()).replace("-","")
        super(Pond, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Farm id={self.id} name={self.name}>"

    def __str__(self):
        return self.__repr__()

    def check_secret(self, secret):
        pass_hash = hashlib.md5(secret.encode('utf8')).hexdigest()
        if self.secret == pass_hash:
            return True
        return False

    def to_json(self):
        rv = {
            "id": self.id,
            "name": self.name,
            "farm_id": self.farm_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return rv
