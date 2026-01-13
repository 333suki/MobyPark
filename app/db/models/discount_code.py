from sqlalchemy import Column, Integer, String, Boolean

from app.db.base import Base


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    percentage = Column(Integer, nullable=False)
    type = Column(String, nullable=False) # "one-time" or "multiple-use"
    used = Column(Boolean, nullable=False, default=False)
