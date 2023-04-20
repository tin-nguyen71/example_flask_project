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


class Device(Base):
    __tablename__ = "device"

    id = Column(String, primary_key=True, default="device-"+str(uuid.uuid4()).replace("-",""))
    pond_id = Column(String, ForeignKey("pond.id", ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=True, default="")

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    def __init__(self, **kwargs):
        # self.id = "device-"+str(uuid.uuid4()).replace("-","")
        if not self.id:
            self.id = "device-"+str(uuid.uuid4()).replace("-","")
        super(Device, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Farm id={self.id} name={self.name}>"

    def __str__(self):
        return self.__repr__()


    def to_json(self):
        rv = {
            "id": self.id,
            "name": self.name,
            "pond_id": self.pond_id,
            "type": self.type,
            "data": self.data
        }
        return rv
