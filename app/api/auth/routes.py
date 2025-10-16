from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User
from datetime import datetime

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

@router.post("/register")
async def register_user(db: Session = Depends(get_db)):
    john = User(username="telmoclaro", password="johndoe", name="John Doe", email="notjohndoe@gmail.com", 
    phone="0611111111", role="User", created_at=datetime.now(), birth_year=1999, active=True)
    db.add(john)
    db.commit()
