from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreate(BaseModel):
    name:  str
    email: str


class UserUpdate(BaseModel):
    name:  Optional[str] = None
    email: Optional[str] = None


def user_to_dict(u: User) -> dict:
    return {
        "id":    u.id,
        "name":  u.name,
        "email": u.email,
        "total_cars": len(u.cars)
    }

@router.post("/", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "id": user.id}


@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    return {"total": len(users), "users": [user_to_dict(u) for u in users]}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    return {"message": "User updated successfully"}


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
