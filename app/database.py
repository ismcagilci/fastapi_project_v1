from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))

with open(f"{basedir}/config.json") as config_file:
        config = json.load(config_file)

SQLALCHEMY_DATABASE_URL = config["sqlalchemy_database_url"]
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()