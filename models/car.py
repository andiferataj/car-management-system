from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Car(Base):
    __tablename__ = "cars"

    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String, nullable=False)
    brand   = Column(String, nullable=False)
    serie   = Column(String, nullable=False)
    year    = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="cars")
