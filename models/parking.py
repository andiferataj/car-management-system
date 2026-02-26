from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class Parking(Base):
    __tablename__ = "parkings"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    location     = Column(String, nullable=False)
    total_spots  = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False)

    cars = relationship("Car", back_populates="parking")
