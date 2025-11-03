from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

router = APIRouter(prefix="/parking_lots", tags=["Parking lots"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ParkingLotsService:
    @staticmethod
    def get_all_parking_lots(db: Session):
        pass

@router.get("/")
async def root():
    return {"message": "Hello Parkinglots!"}
