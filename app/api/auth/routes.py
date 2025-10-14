from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User

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
