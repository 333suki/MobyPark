from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

from app.db.base import Base


class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    license_plate = Column(String, nullable=False)
    started = Column(DateTime, nullable=False)
    stopped = Column(DateTime)
    username = Column(String, nullable=False)
    duration_minutes = Column(Integer)
    cost = Column(Float)
    payment_status = Column(String, nullable=False)
