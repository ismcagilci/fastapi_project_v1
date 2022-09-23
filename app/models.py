from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Date
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime,timezone
from sqlalchemy_serializer import SerializerMixin

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable = False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey('users.id',ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), unique=True, index=True)
    is_archived = Column(Boolean,default = False)
    created_date = Column(Date, nullable=False, default=datetime.now(timezone.utc))

    current_user = relationship('User')


class WorkHistory(Base):
    __tablename__ = "work_history"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(ForeignKey('project.id',ondelete="CASCADE"), nullable=True, index=True)
    header = Column(String(255), unique=True, index=True)
    created_date = Column(Date, default=datetime.now(timezone.utc))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status =  Column(String(100), default="Received")

    current_project = relationship('Project')


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, index=True)
    work_history_id = Column(ForeignKey('work_history.id',ondelete="CASCADE"), nullable=True, index=True)
    content = Column(String(255), nullable= False)
    created_date = Column(Date, nullable=False, default=datetime.now(timezone.utc))

    current_work_history = relationship('WorkHistory')


