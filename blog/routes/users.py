
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from blog.schemas import LoginRequest
from blog import models, schemas, auth
from blog.db import get_db
from blog.models import Log

router = APIRouter(tags=["Users"])



@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

  
    log = Log(user_id=new_user.id, table_name ="users")
    db.add(log)
    db.commit()

    return new_user




@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    email = credentials.email
    password = credentials.password

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_data = {"sub": str(user.id)}
    token = auth.create_access_token(token_data)

    
    log = Log(user_id=user.id, table_name ="users")
    db.add(log)
    db.commit()

    return {"access_token": token, "token_type": "bearer"}



