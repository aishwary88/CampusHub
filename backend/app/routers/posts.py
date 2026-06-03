from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostRead
from app.services import post_service
from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/", response_model=List[PostRead])
def get_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return post_service.get_posts(db, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/", response_model=PostRead, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return post_service.create_post(db, post, author_id=current_user.id)

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = post_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    post_service.delete_post(db, post_id)
