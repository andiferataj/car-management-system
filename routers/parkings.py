from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.parking import Parking

router = APIRouter(prefix="/parkings", tags=["Parkings"])


class ParkingCreate(BaseModel):
    name:            str
    location:        str
    total_spots:     int
    price_per_hour:  float


class ParkingUpdate(BaseModel):
    name:            Optional[str]   = None
    location:        Optional[str]   = None
    total_spots:     Optional[int]   = None
    price_per_hour:  Optional[float] = None


def parking_to_dict(p: Parking) -> dict:
    return {
        "id":             p.id,
        "name":           p.name,
        "location":       p.location,
        "total_spots":    p.total_spots,
        "price_per_hour": p.price_per_hour,
        "cars_parked":    len(p.cars)
    }


# CREATE
@router.post("/", status_code=201)
def create_parking(payload: ParkingCreate, db: Session = Depends(get_db)):
    parking = Parking(**payload.model_dump())
    db.add(parking)
    db.commit()
    db.refresh(parking)
    return {"message": "Parking created successfully", "id": parking.id}


# READ ALL
@router.get("/")
def get_all_parkings(db: Session = Depends(get_db)):
    parkings = db.query(Parking).all()
    return {"total": len(parkings), "parkings": [parking_to_dict(p) for p in parkings]}


# READ ONE
@router.get("/{parking_id}")
def get_parking(parking_id: int, db: Session = Depends(get_db)):
    parking = db.query(Parking).filter(Parking.id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return parking_to_dict(parking)


# UPDATE
@router.put("/{parking_id}")
def update_parking(parking_id: int, payload: ParkingUpdate, db: Session = Depends(get_db)):
    parking = db.query(Parking).filter(Parking.id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(parking, field, value)
    db.commit()
    return {"message": "Parking updated successfully"}


# DELETE
@router.delete("/{parking_id}")
def delete_parking(parking_id: int, db: Session = Depends(get_db)):
    parking = db.query(Parking).filter(Parking.id == parking_id).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    db.delete(parking)
    db.commit()
    return {"message": "Parking deleted successfully"}
