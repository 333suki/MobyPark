from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def root(db: Session = Depends(get_db)):
    return db.query(User).all()
    

