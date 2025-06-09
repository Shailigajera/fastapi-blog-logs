from pydantic import BaseModel, EmailStr
from typing import List , Optional
from datetime import datetime

class UserBase(BaseModel):
    username:str
    email :str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id:int

    class Config :
        orm_mode =True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class BlogBase(BaseModel):
    title:str
    content:str

class BlogCreate(BlogBase):
    pass

class BLogUpdate(BlogBase):
    pass

class BlogResponse(BlogBase):
    id:int
    user_id:int
    created_at:datetime

    class Config:
        orm_mode =True



class LogBase(BaseModel):
    id:int
    user_id :int
    table_name:str
    timestamp:datetime

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content : str

class CommentCreate(CommentBase):
    blog_id : int

class CommentUpdate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id:int
    user_id:int
    blog_id:int
    created_at:datetime

    class Config:
        orm_mode = True