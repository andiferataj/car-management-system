from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    email    = Column(String, unique=True, nullable=False)

    cars = relationship("Car", back_populates="owner")
