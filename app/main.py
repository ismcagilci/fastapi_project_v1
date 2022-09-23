from typing import List,Union

from datetime import timedelta,datetime,date
from fastapi import Depends, FastAPI, HTTPException,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from . import models,crud,schemas
from .database import SessionLocal, engine

from jose import JWTError, jwt

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
from celery import Celery


models.Base.metadata.create_all(bind=engine)

basedir = os.path.abspath(os.path.dirname(__file__))
with open(f"{basedir}/config.json") as config_file:
        config = json.load(config_file)

SECRET_KEY = config["secret_key"]
ALGORITHM = config["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = config["access_token_expire_minutes"]
SLACK_BOT_TOKEN = config["slack_bot_token"]
SLACK_CHANNEL_NAME = config["slack_channel_name"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token,db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id : str = payload.get("user_id")

        check_user = db.query(models.User).filter(models.User.id == user_id).first()
        if user_id is None or check_user == False:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
    




app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def drop_db():
    db = SessionLocal()
    try:
        db.session.remove()
        db.drop_all()
    finally:
        db.close()



@app.post("/register/")
def register_user(user:schemas.User,db: Session = Depends(get_db)):
    return crud.register_user(db, user)



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@app.post("/login/")
def login_user(user:schemas.User,db: Session = Depends(get_db)):
    check_user = db.query(models.User).filter_by(email = user.email).first()
    if not check_user:
        return {"error":"User is not found"}
    if check_user.verify_hash(user.password,check_user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_email": check_user.email,"user_id":check_user.id,"username":check_user.username}, expires_delta=access_token_expires
        )
        return {
            "message":"User successfully logged in!",
            "access_token": access_token,
            "token_type": "bearer",
            "expire_time(seconds)":access_token_expires
            }
    else:
        return {"error":"Password is not correct"}

@app.get("/users/")
def get_users(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    users = crud.get_users(db)
    return users

#PROJECTS
@app.post("/projects/")
def create_project(project:schemas.Project,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    check_project = db.query(models.Project).filter(models.Project.name == project.name).first()
    if check_project:
        return {"error":"There is already a project with same name"}
    else:
        get_user = db.query(models.User).filter(models.User.id == payload.get("user_id")).first()
        new_project = models.Project(
            name = project.name,
            user_id = payload.get("user_id"),
            current_user = get_user
        )
        db.add(new_project)
        db.commit()
        return {
            "message":"Project was created successfully"
        }

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_projects = db.query(models.Project).filter(models.Project.user_id == payload.get("user_id")).all()
    return get_projects


#PROJECT
@app.patch("/project/{project_id}")
def patch_project(project:schemas.Project,project_id,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if get_project:
        if project.name:
            get_project.name = project.name
        if project.is_archived:
            get_project.is_archived = is_archived
        db.add(get_project)
        db.commit()
        return {
            "success":"Project was updated",
        }
    else:
        return {"error":"There is no project for this id"}

@app.get("/project/{project_id}")
def get_project(project_id,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_project = db.query(models.Project).filter(models.Project.id == project_id).all()
    return get_project
    


#WORK HISTORIES
@app.post("/work_histories/{project_id}")
def create_work_history(project_id,work_history:schemas.WorkHistory,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    check_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not check_project:
        return {"error":"There is no project for this id"}
    check_work_history = db.query(models.WorkHistory).filter(models.WorkHistory.header == work_history.header).first()
    if check_work_history:
        return {"error":"There is already a project with same header"}
    else:
        new_work_history = models.WorkHistory(
            header = work_history.header,
            start_date = work_history.start_date,
            end_date = work_history.end_date,
            status = work_history.status,
            project_id = project_id,
            current_project = check_project
        )
        db.add(new_work_history)
        db.commit()
        return {
            "message":"Work History was created successfully"
        }

@app.get("/work_histories/{project_id}")
def get_work_histories(project_id,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_work_histories = db.query(models.WorkHistory).filter(models.WorkHistory.project_id == project_id).all()
    return get_work_histories


#WORK HISTORY
@app.get("/work_history/{work_history_id}")
def get_work_history(work_history_id,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_work_history = db.query(models.WorkHistory).filter(models.WorkHistory.id == work_history_id).all()
    return get_work_history


#COMMENTS
@app.post("/comments/{work_history_id}")
def create_comment(work_history_id,comment:schemas.Comment,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    check_work_history = db.query(models.WorkHistory).filter(models.WorkHistory.id == work_history_id).first()
    if not check_work_history:
        return {"error":"There is no work history for this id"}
    else:
        new_comment = models.Comment(
            content = comment.content,
            work_history_id = work_history_id,
            current_work_history = check_work_history
        )
        db.add(new_comment)
        db.commit()
        return {
            "message":"Comment was created successfully"
        }

@app.get("/comments/{work_history_id}")
def get_work_histories(work_history_id,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    get_comments = db.query(models.Comment).filter(models.Comment.work_history_id == work_history_id).all()
    return get_comments


#CHECK WORK HISTORY
@app.get("/check_work_histories")
def check_work_histories(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    payload = verify_token(token,db)
    all_work_histories = db.query(models.WorkHistory).all()
    client = WebClient(token=SLACK_BOT_TOKEN)
    for work_history in all_work_histories:
        now = date.today()
        if work_history.start_date:
            if work_history.start_date < now and work_history.status != "is_started":
                message_text = f"Although the start time has passed, the status of the work history with {work_history.id}(id_number) has not changed to 'is_started'"
                try:
                    response = client.chat_postMessage(channel=SLACK_CHANNEL_NAME, text=message_text)
                    return {"success":"All work histories was checked"}

                except SlackApiError as e:
                    return {"Slack_API_Error":e}
        if work_history.end_date:
            if work_history.end_date < now and work_history.status != "is_ended":
                message_text = f"Although the end_time has passed, the status of the work history with {work_history.id}(id_number) has not changed to 'is_ended'"
                try:
                    response = client.chat_postMessage(channel=SLACK_CHANNEL_NAME, text=message_text)
                    return {"success":"All work histories was checked"}
                except SlackApiError as e:
                    return {"Slack_API_Error":e}