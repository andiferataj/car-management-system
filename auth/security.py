import hashlib
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db


def hash_password(plain: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(plain.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plain password against its SHA-256 hash."""
    return hash_password(plain) == hashed


def get_current_user(username: str, db: Session = Depends(get_db)):
    """Look up a user by username or raise 404."""
    from models.user import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
