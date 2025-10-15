from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from db.base import Base

class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    license_plate = Column(String, nullable=False)
    started = Column(Date, nullable=False)
    stopped = Column(Date)
    username = Column(String, nullable=False)
    duration_minutes = Column(Integer)
    cost = Column(Float)
    payment_status = Column(String, nullable=False)
