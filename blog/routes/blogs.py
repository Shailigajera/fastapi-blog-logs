
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List

from blog import models, schemas, auth
from blog.db import get_db
from blog.models import Log
from blog.auth import get_token_payload
router = APIRouter(tags=["Blogs"])


def get_current_user(token_payload: dict = Depends(get_token_payload), db: Session = Depends(get_db)):
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




@router.post("/", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_blog = models.Blog(
        title=blog.title,
        content=blog.content,
        user_id=current_user.id
    )
    print(new_blog)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    log = Log(user_id=current_user.id, table_name='blogs')
    db.add(log)
    db.commit()

    return new_blog

@router.get("/", response_model=List[schemas.BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs




@router.get("/user/{user_id}", response_model=List[schemas.BlogResponse])
def get_blogs_by_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    blogs = db.query(models.Blog).filter(models.Blog.user_id == user_id).all()
    

    if not blogs:
        raise HTTPException(status_code=404, detail="No blogs found for this user")

    return blogs


@router.put("/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(blog_id: int, updated_blog: schemas.BlogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this blog")

    blog.title = updated_blog.title
    blog.content = updated_blog.content
    db.commit()
    db.refresh(blog)

    log = Log(user_id=current_user.id, table_name='blogs')
    db.add(log)
    db.commit()
    return blog

@router.delete("/{blog_id}", status_code=status.HTTP_200_OK)
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this blog")

    db.delete(blog)
    db.commit()

    log = Log(user_id=current_user.id, table_name='blogs')
    db.add(log)
    db.commit()

    return {"detail": "Blog deleted successfully"}