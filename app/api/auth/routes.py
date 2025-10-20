from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authorization"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# http://127.0.0.1:8000/auth/
@router.get("/")
async def root(db: Session = Depends(get_db)):
    return db.query(User).all()

class User(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    role: str
    created_at: date
    birth_year: int
    active: bool

@router.post("/register")
async def register_user(db: Session = Depends(get_db), user: User):
    db.add(user)
    db.commit()
    return 200
