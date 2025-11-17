from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey

from app.db.base import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    license_plate = Column(String, nullable=False)
    start_time = Column(Date, nullable=False)
    end_time = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
    cost = Column(Float, nullable=False)
