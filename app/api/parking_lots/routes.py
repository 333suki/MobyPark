from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.models.parking_lot import ParkingLot
from app.db.database import SessionLocal
from app.api.login_sessions.session_manager import LoginSessionManager

router = APIRouter(prefix="/parking_lots", tags=["Parking lots"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ParkingLotsService:
    @staticmethod
    def get_all_parking_lots(
        db: Session,
        limit: Optional[int] = None,
        parking_lot_id: Optional[int] = None,
        parking_lot_name: Optional[str] = None,
        location: Optional[str] = None,
        address: Optional[str] = None,
        creation_date: Optional[datetime] = None
    ):
        query = db.query(ParkingLot)
        if parking_lot_id:
            query = query.filter(ParkingLot.id == parking_lot_id)
        if parking_lot_name:
            query = query.filter(ParkingLot.name == parking_lot_name)
        if location:
            query = query.filter(ParkingLot.location == location)
        if address:
            query = query.filter(ParkingLot.address == address)
        if creation_date:
            query = query.filter(ParkingLot.created_at == creation_date)

        if limit:
            return query.order_by(ParkingLot.id).limit(limit).all()
        return query.order_by(ParkingLot.id).all()

@router.get("/")
async def get_parking_lots(
        request: Request,
        limit: Optional[int] = Query(None, description="Limit the amount of results", ge=1),
        parking_lot_id: Optional[int] = Query(None, description="Filter by parking lot ID"),
        parking_lot_name: Optional[str] = Query(None, description="Filter by parking lot name"),
        location: Optional[str] = Query(None, description="Filter by parking lot location"),
        address: Optional[str] = Query(None, description="Filter by parking lot address"),
        creation_date: Optional[datetime] = Query(None, description="Filter by parking lot creation date (YYYY-MM-DD)"),
        db: Session = Depends(get_db)
):
    # Validate token
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )

    # Get user info
    user_id = LoginSessionManager.get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # TODO: Continue
    return {"message": "Hello Parkinglots!"}
