from fastapi import FastAPI
from blog.db import Base, engine
from blog.routes import users, blogs, comments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Blog System")

app.include_router(users.router, prefix="/users")
app.include_router(blogs.router, prefix="/blogs")
app.include_router(comments.router, prefix="/comments")


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Blog System!"}
