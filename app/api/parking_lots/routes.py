from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.api.parking_lots.schemas import ParkingLotsResponse, CreateParkingLotBody, UpdateParkingLotBody
from app.db.database import SessionLocal
from app.db.models.parking_lot import ParkingLot

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
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenInvalidError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    user_id: int = user_info.get("sub")
    user_role: str = user_info.get("role")

    return ParkingLotsService.get_all_parking_lots(db, limit, parking_lot_id, parking_lot_name, parking_lot_location,
                                                   parking_lot_address, parking_lot_capacity, parking_lot_reserved,
                                                   parking_lot_tariff, parking_lot_daytariff, parking_lot_creation_date)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(request: Request, body: CreateParkingLotBody, db: Session = Depends(get_db)):
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenInvalidError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    role: str = user_info.get("role")

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

@router.put("/{parking_lot_id}", status_code=status.HTTP_200_OK)
async def update_parking_lot(parking_lot_id: int, request: Request, body: Optional[UpdateParkingLotBody], db: Session = Depends(get_db)):
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body"
        )

    parking_lot: ParkingLot | None = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
    if parking_lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking lot with ID {parking_lot_id} not found."
        )

    if body.name:
        parking_lot.name = body.name
    if body.location:
        parking_lot.location = body.location
    if body.address:
        parking_lot.address = body.address
    if body.capacity:
        parking_lot.capacity = body.capacity
    if body.reserved:
        parking_lot.reserved = body.reserved
    if body.tariff:
        parking_lot.tariff = body.tariff
    if body.daytariff:
        parking_lot.daytariff = body.daytariff
    if body.coordinates_lng:
        parking_lot.coordinates_lng = body.coordinates_lng
    if body.coordinates_lat:
        parking_lot.coordinates_lat = body.coordinates_lat

    db.commit()
    return {"message": "Parking lot updated successfully"}

@router.delete("/{parking_lot_id}", status_code=status.HTTP_200_OK)
async def delete_parking_lot(parking_lot_id: int, request: Request, db: Session = Depends(get_db)):
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    if db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).delete() == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking lot with ID {parking_lot_id} not found."
        )

    db.commit()
    return {"message": "Parking lot deleted successfully"}
