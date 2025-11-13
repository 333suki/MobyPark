from sqlalchemy import Column, Integer, String, Float, Date

from app.db.base import Base


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    address = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    reserved = Column(Integer, nullable=False)
    tariff = Column(Float, nullable=False)
    daytariff = Column(Integer, nullable=False)
    created_at = Column(Date, nullable=False)
    coordinates_lat = Column(Float, nullable=False)
    coordinates_lng = Column(Float, nullable=False)
