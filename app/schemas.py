from pydantic import BaseModel

from typing import Union,Optional

class Token(BaseModel):
    message: str
    access_token: str
    token_type: str
    expire_time: int




class User(BaseModel):
    email: str
    password: str
    username: str

class Project(BaseModel):
    name: Optional[str] = None
    is_archived : Optional[bool] = None

class WorkHistory(BaseModel):
    header: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None

class Comment(BaseModel):
    content: str