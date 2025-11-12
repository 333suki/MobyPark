from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Date
from datetime import datetime

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    transaction = Column(String, index=True)
    amount = Column(Float, nullable=False)
    initiator_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    completed = Column(DateTime, nullable=True)
    hash = Column(String, nullable=False, index=True)
    t_data_id = Column(Integer, nullable=True, primary_key=True)
    parking_session_id = Column(Integer, ForeignKey("parking_sessions.id"), nullable=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=True)
