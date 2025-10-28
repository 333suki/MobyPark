from sqlalchemy import Column, Integer, String, Date, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)
    name = Column(String, unique=False, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=False, nullable=False)
    role = Column(String, unique=False, nullable=False)
    created_at = Column(Date, unique=False, nullable=False)
    birth_year = Column(Integer, unique=False, nullable=False)
    active = Column(Boolean, default=True, unique=False, nullable=False)
