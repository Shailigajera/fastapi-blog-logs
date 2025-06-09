from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text,func
from sqlalchemy.orm import relationship
from blog.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key =True , index=True)
    username=Column(String, nullable=False)
    email=Column(String,unique=True,index=True)
    password=Column(String,nullable=False)

    blogs=relationship("Blog", back_populates='user')
    comments=relationship("Comment", back_populates='user')
    logs=relationship("Log", back_populates="user")

class Blog(Base):
    __tablename__ = "blogs"

    id =Column(Integer, primary_key=True, index=True)
    title =Column(String, nullable=False)
    content =Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id =Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog")
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True ,index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id =Column(Integer, ForeignKey("users.id"))
    table_name =Column(String, nullable=False)

    user = relationship("User", back_populates='logs')


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content =Column(Text,nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))


    user = relationship("User", back_populates='comments')
    blog = relationship("Blog", back_populates='comments')
    