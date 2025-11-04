from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.models.parking_lot import ParkingLot
from app.db.database import SessionLocal
from app.api.login_sessions.session_manager import LoginSessionManager
from app.util.db_utils import DbUtils
from app.api.parking_lots.schemas import ParkingLotsResponse, CreateParkingLotBody

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
            parking_lot_location: Optional[str] = None,
            parking_lot_address: Optional[str] = None,
            parking_lot_capacity: Optional[str] = None,
            parking_lot_reserved: Optional[int] = None,
            parking_lot_tariff: Optional[float] = None,
            parking_lot_daytariff: Optional[str] = None,
            parking_lot_creation_date: Optional[datetime] = None
    ):
        query = db.query(ParkingLot)
        if parking_lot_id:
            query = query.filter(ParkingLot.id == parking_lot_id)
        if parking_lot_name:
            query = query.filter(ParkingLot.name == parking_lot_name)
        if parking_lot_location:
            query = query.filter(ParkingLot.location == parking_lot_location)
        if parking_lot_address:
            query = query.filter(ParkingLot.address == parking_lot_address)
        if parking_lot_capacity:
            query = query.filter(ParkingLot.capacity == parking_lot_capacity)
        if parking_lot_reserved:
            query = query.filter(ParkingLot.reserved == parking_lot_reserved)
        if parking_lot_tariff:
            query = query.filter(ParkingLot.tariff == parking_lot_tariff)
        if parking_lot_daytariff:
            query = query.filter(ParkingLot.daytariff == parking_lot_daytariff)
        if parking_lot_creation_date:
            query = query.filter(ParkingLot.created_at == parking_lot_creation_date)

        if limit:
            return query.order_by(ParkingLot.id).limit(limit).all()
        return query.order_by(ParkingLot.id).all()

@router.get("/", response_model=List[ParkingLotsResponse])
async def get_parking_lots(
        request: Request,
        limit: Optional[int] = Query(None, description="Limit the amount of results", ge=1),
        parking_lot_id: Optional[int] = Query(None, description="Filter by parking lot ID"),
        parking_lot_name: Optional[str] = Query(None, description="Filter by parking lot name"),
        parking_lot_location: Optional[str] = Query(None, description="Filter by parking lot location"),
        parking_lot_address: Optional[str] = Query(None, description="Filter by parking lot address"),
        parking_lot_capacity: Optional[str] = Query(None, description="Filter by parking lot capacity"),
        parking_lot_reserved: Optional[int] = Query(None, description="Filter by parking lot reserved spot count"),
        parking_lot_tariff: Optional[float] = Query(None, description="Filter by parking lot tariff"),
        parking_lot_daytariff: Optional[str] = Query(None, description="Filter by parking lot day tariff"),
        parking_lot_creation_date: Optional[datetime] = Query(None, description="Filter by parking lot creation date (YYYY-MM-DD)"),
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

    return ParkingLotsService.get_all_parking_lots(db, limit, parking_lot_id, parking_lot_name, parking_lot_location,
                                                   parking_lot_address, parking_lot_capacity, parking_lot_reserved,
                                                   parking_lot_tariff, parking_lot_daytariff, parking_lot_creation_date)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(request: Request, body: CreateParkingLotBody, db: Session = Depends(get_db)):
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

    # Get role
    role = DbUtils.get_user_role(db, user_id)
    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    parking_lot: ParkingLot = ParkingLot(
        name = body.name,
        location = body.location,
        address = body.address,
        capacity = body.capacity,
        reserved = body.reserved,
        tariff = body.tariff,
        daytariff = body.daytariff,
        created_at = datetime.now(),
        coordinates_lat = body.coordinates_lat,
        coordinates_lng = body.coordinates_lng
    )

    db.add(parking_lot)
    db.commit()

    return { "message": "Parking lot created successfully" }
