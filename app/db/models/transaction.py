from sqlalchemy import Column, Integer, String, Float, Date

from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    method = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    bank = Column(String, nullable=False)
