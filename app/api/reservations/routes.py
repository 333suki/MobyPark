from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Request, Query, Body
from sqlalchemy.orm import Session

from app.api.reservations.schemas import ReservationCreate, ReservationUpdate
from app.db.database import SessionLocal
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.util.reservation_utils import ReservationUtils

from app.db.models.reservation import Reservation
from app.db.models.parking_lot import ParkingLot


router = APIRouter(prefix="/reservations", tags=["Reservations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ReservationsService:
    @staticmethod
    def get_all_reservations(
            db: Session,
            limit: Optional[int] = None,
            reservation_id: Optional[int] = None,
            user_id: Optional[int] = None,
            parking_lot_id: Optional[int] = None,
            license_plate: Optional[str] = None,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            reservation_status: Optional[str] = None,
            created_at: Optional[datetime] = None,
            cost: Optional[float] = None
    ):
        query = db.query(Reservation)
        if reservation_id:
            query = query.filter(Reservation.id == reservation_id)
        if user_id:
            query = query.filter(Reservation.user_id == user_id)
        if parking_lot_id:
            query = query.filter(Reservation.parking_lot_id == parking_lot_id)
        if license_plate:
            query = query.filter(Reservation.license_plate == license_plate)
        if start_time:
            query = query.filter(Reservation.start_time == start_time)
        if end_time:
            query = query.filter(Reservation.end_time == end_time)
        if reservation_status:
            query = query.filter(Reservation.status == reservation_status)
        if created_at:
            query = query.filter(Reservation.created_at == created_at)
        if cost:
            query = query.filter(Reservation.cost == cost)

        if limit:
            return query.order_by(Reservation.id).limit(limit).all()
        return query.order_by(Reservation.id).all()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_reservations(
        request: Request,
        limit: Optional[int] = Query(None, description="Limit the amount of results", ge=1),
        reservation_id: Optional[int] = Query(None, description="Filter by reservation ID"),
        user_id: Optional[int] = Query(None, description="Filter by user ID"),
        parking_lot_id: Optional[int] = Query(None, description="Filter by parking lot ID"),
        license_plate: Optional[str] = Query(None, description="Filter by license plate"),
        start_time: Optional[datetime] = Query(None, description="Filter by starting time"),
        end_time: Optional[datetime] = Query(None, description="Filter by end time"),
        reservation_status: Optional[str] = Query(None, description="Filter by status"),
        created_at: Optional[datetime] = Query(None, description="Filter by creation date"),
        cost: Optional[float] = Query(None, description="Filter by cost"),
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

    # If non-admin tries to get reservations from a user that is not himself
    # Set the filter to his own ID
    if user_info.get("role").lower() != "admin" and user_id != user_info.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User cannot view reservations of other users"
        )

    return ReservationsService.get_all_reservations(db, limit, reservation_id, user_id, parking_lot_id, license_plate,
                                                    start_time, end_time, reservation_status, created_at, cost)

@router.post("/", status_code=status.HTTP_200_OK)
async def create_reservation(request: Request, body: Optional[ReservationCreate] = Body(None), db: Session = Depends(get_db)):
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

    # Check if there is no body provided
    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body"
        )
    
    # Check if the body is empty
    if all(value is None for value in body.dict().values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body"
        )
    
    role: str = user_info.get("role")
    user_id: int = user_info.get("sub")

    # If the userid is not none, the user is trying to make a reservation for another user, only admin can do this
    if role.lower() == "admin" and body.user_id is not None:
        user_id = body.user_id
    
    # db queries to calculate the parking session tariffs
    parking_lot = db.query(ParkingLot).filter(
        ParkingLot.id == body.parking_lot_id
    ).first()

    if parking_lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking lot not found"
        )

    # If theres a cost in the request
    if role.lower() == "admin" and body.cost is not None:
        total_cost = body.cost
    else: 
        total_cost = ReservationUtils.calculate_price(parking_lot, body.start_time, body.end_time)

    # If theres a status in the request 
    if role.lower() == "admin" and body.status is not None:
        reservation_status = body.status
    else:
        reservation_status = "pending"

    # Create a reservation
    reservation: Reservation = Reservation(
    user_id = user_id,
    parking_lot_id = body.parking_lot_id,
    license_plate = body.license_plate,
    start_time = body.start_time,
    end_time = body.end_time,
    status = reservation_status,
    created_at = datetime.now(),
    cost = total_cost
    )

    db.add(reservation)
    db.commit()

    return { "message": "Reservation created succesfully" }

@router.put("/{reservation_id}", status_code=status.HTTP_200_OK)
async def update_reservation(reservation_id: int, request: Request, body: Optional[ReservationUpdate] = Body(None), db: Session = Depends(get_db)):
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

    # Check if there is no body provided
    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body"
        )

    # Check if the body is empty
    if all(value is None for value in body.dict().values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body"
        )

    role: str = user_info.get("role")
    user_id: int = user_info.get("sub")

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    parking_lot = db.query(ParkingLot).filter(
        ParkingLot.id == body.parking_lot_id
    ).first()

    if parking_lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking lot not found"
        )
    
    if user_id != Reservation.user_id and role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Users can only update own reservation"
        )

    if body.parking_lot_id:
        reservation.parking_lot_id = body.parking_lot_id
    if body.license_plate:
        reservation.license_plate = body.license_plate
    if body.start_time:
        reservation.start_time = body.start_time
        reservation.cost = ReservationUtils.calculate_price(parking_lot, body.start_time, body.end_time)
    if body.end_time:
        reservation.end_time = body.end_time
        reservation.cost = ReservationUtils.calculate_price(parking_lot, body.start_time, body.end_time)
    if body.status and role.lower() == "admin":
        reservation.status = body.status
    if body.cost and role.lower() == "admin":
        reservation.cost = body.cost

    db.commit()
    return { "message": "Reservation updated successfully"}

@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
async def update_reservation(reservation_id: int, request: Request,db: Session = Depends(get_db)):
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
    user_id: int = user_info.get("sub")

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    if user_id != Reservation.user_id and role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Users can only delete own reservation"
        )

    if db.query(Reservation).filter(Reservation.id == reservation_id).delete() == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation lot with ID {reservation_id} not found."
        )

    db.commit()
    return {"message": "Reservation deleted successfully"}