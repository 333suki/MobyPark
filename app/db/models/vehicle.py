from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db.base import Base

class Vehicle(base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_plate = Column(String, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    year = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
