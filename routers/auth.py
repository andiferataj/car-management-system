from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from auth.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email:    str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "id": user.id}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login with username and password."""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"message": "Login successful", "user_id": user.id, "username": user.username}
