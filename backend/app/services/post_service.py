from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate


def get_posts(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Post).offset(skip).limit(limit).all()


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(db: Session, post: PostCreate, author_id: int):
    db_post = Post(
        title=post.title,
        content=post.content,
        is_published=post.is_published,
        author_id=author_id,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
