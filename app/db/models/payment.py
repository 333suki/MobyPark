from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    transaction = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    initiator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(Date, nullable=False)
    completed = Column(Date, nullable=False)
    hash = Column(String, nullable=False)
    t_data_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    parking_session_id = Column(Integer, ForeignKey("parking_sessions.id"), nullable=False)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
