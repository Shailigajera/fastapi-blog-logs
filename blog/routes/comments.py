from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List

from blog import models, schemas, auth
from blog.db import get_db
from blog.models import Log
from blog.auth import get_token_payload

router = APIRouter(tags=["Comments"])



def get_current_user(token_payload: dict = Depends(get_token_payload), db: Session = Depends(get_db)):
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=schemas.CommentResponse)
def add_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    blog = db.query(models.Blog).filter(models.Blog.id == comment.blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    new_comment = models.Comment(
        content=comment.content,
        blog_id=comment.blog_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    log = Log(user_id=current_user.id, table_name='comments')
    db.add(log)
    db.commit()

    return new_comment

@router.get("/blogs/{blog_id}", response_model=List[schemas.CommentResponse])
def get_comments_by_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments found")

    return comments


@router.get("/user/{user_id}", response_model=List[schemas.CommentResponse])
def get_comments_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these comments")

    comments = db.query(models.Comment).filter(models.Comment.user_id == user_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="No comments by this user")

    return comments

@router.put("/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    comment_id: int,
    updated_content: schemas.CommentBase,  
    blog_id: int = Header(...),            
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    if comment.blog_id != blog_id:
        raise HTTPException(status_code=400, detail="Incorrect blog ID")

    comment.content = updated_content.content
    db.commit()
    db.refresh(comment)

    log = Log(user_id=current_user.id, table_name='comments')
    db.add(log)
    db.commit()

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    blog = db.query(models.Blog).filter(models.Blog.id == comment.blog_id).first()
    if comment.user_id != current_user.id and blog.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

    log = Log(user_id=current_user.id, table_name='comments')
    db.add(log)
    db.commit()

    return {"detail": "Comment deleted successfully"}



