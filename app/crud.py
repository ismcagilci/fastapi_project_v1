
from sqlalchemy.orm import Session
from typing import List,Union

from . import models,schemas
from datetime import timedelta,datetime
from fastapi import Depends,HTTPException,status
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm





def register_user(db:Session,user:schemas.User):
    check_user = db.query(models.User).filter_by(email = user.email).first()
    if not check_user:
        new_user = models.User(
            email = user.email,
            username = user.username,
            password = models.User.generate_hash(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success":"User was created successfully"}
    else:
        return {"error":"User is already exists"}


def get_users(db: Session):
    return db.query(models.User).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

