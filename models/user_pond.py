import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, String, JSON, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from system.database_uuid import UUID
from system.model_base import Base


class UserPond(Base):
    __tablename__ = "user_pond"

    # id = Column(String, primary_key=True, default="up-"+str(uuid.uuid4()).replace("-",""))
    pond_id = Column(String, ForeignKey("pond.id", ondelete='CASCADE'), nullable=False, primary_key=True)
    client_id = Column(String, ForeignKey("vmq_auth_acl.client_id", ondelete='CASCADE'), nullable=False, primary_key=True)
    role_admin = Column(Boolean, default=False, nullable=False)
    role_update = Column(Boolean, default=False, nullable=False)
    role_view = Column(Boolean, default=True, nullable=False)
    
    pond = relationship("Pond", lazy='select')
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    def __init__(self, **kwargs):
        self.id = "up-"+str(uuid.uuid4()).replace("-","")
        super(UserPond, self).__init__(**kwargs)

    def __repr__(self):
        return f"<UserFarm id={self.id} farmID={self.farm_id} >"

    def __str__(self):
        return self.__repr__()

    def to_json(self):
        rv = {
            "pond_id": self.pond_id,
            "client_id": self.client_id,
            "role_admin": self.role_admin,
            "role_update": self.role_update,
            "role_view": self.role_view
        }
        return rv
