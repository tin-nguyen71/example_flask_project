import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from env_config import get_config_docker
from system.model_util import JsonSerializer, ModelGeneralTasks, GeneralQuery

# engine = create_engine(get_config_docker("SQLALCHEMY_DATABASE_URI"))
DB_URL = os.getenv("DB_URL")
db_connection_string = f"mysql+pymysql://vernemq:vernemq@{DB_URL}/vernemq_db"
engine = create_engine(db_connection_string)

Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base(bind=engine, cls=(JsonSerializer, ModelGeneralTasks))
Base.query = Session.query_property(GeneralQuery)
