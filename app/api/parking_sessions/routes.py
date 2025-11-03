from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc
from datetime import datetime

from app.db.database import SessionLocal
from app.db.models.parking_session import ParkingSession
from app.db.models.user import User
from app.api.login_sessions.session_manager import LoginSessionManager
from .schemas import ParkingSessionResponse

router = APIRouter(prefix="/parking_sessions", tags=["parking_sessions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ParkingSessionService:
    @staticmethod
    def get_user_sessions(
        db: Session,
        username: str,
        limit: int = 100,
        parking_lot_id: Optional[int] = None,
        license_plate: Optional[str] = None,
        date: Optional[datetime] = None,
        search_username: Optional[str] = None
    ):
        query = db.query(ParkingSession).filter(ParkingSession.username == username)
        query = ParkingSessionService.apply_filters(
            query, parking_lot_id, license_plate, date, search_username
        )
        return query.order_by(desc(ParkingSession.started)).limit(limit).all()

    @staticmethod
    def get_all_sessions(
        db: Session,
        limit: int = 100,
        parking_lot_id: Optional[int] = None,
        license_plate: Optional[str] = None,
        date: Optional[datetime] = None,
        search_username: Optional[str] = None
    ):
        query = db.query(ParkingSession)
        query = ParkingSessionService.apply_filters(
            query, parking_lot_id, license_plate, date, search_username
        )
        return query.order_by(desc(ParkingSession.started)).limit(limit).all()

    @staticmethod
    def apply_filters(
        query,
        parking_lot_id: Optional[int] = None,
        license_plate: Optional[str] = None,
        date: Optional[datetime] = None,
        search_username: Optional[str] = None
    ):
        if parking_lot_id:
            query = query.filter(ParkingSession.parking_lot_id == parking_lot_id)
        if license_plate:
            query = query.filter(ParkingSession.license_plate.ilike(f"%{license_plate}%"))
        if date:
            query = query.filter(
                ParkingSession.started >= date.replace(hour=0, minute=0, second=0),
                ParkingSession.started < date.replace(hour=23, minute=59, second=59)
            )
        if search_username:
            query = query.filter(ParkingSession.username.ilike(f"%{search_username}%"))
        return query

    @staticmethod
    def get_user_role(db: Session, user_id: int) -> str:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user.role

    @staticmethod
    def get_username(db: Session, user_id: int) -> str | None:
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else None

@router.get("/", response_model=List[ParkingSessionResponse])
async def get_parking_sessions(
    request: Request,
    limit: int = Query(default=100, ge=1, le=1000),
    parking_lot_id: Optional[int] = Query(None, description="Filter by parking lot ID"),
    license_plate: Optional[str] = Query(None, description="Filter by license plate"),
    date: Optional[datetime] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    search_username: Optional[str] = Query(None, description="Filter by username"),
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

    # Get role and username
    role = ParkingSessionService.get_user_role(db, user_id)
    username = ParkingSessionService.get_username(db, user_id)

    # Return sessions based on role
    if role.lower() == "admin":
        sessions = ParkingSessionService.get_all_sessions(
            db, limit, parking_lot_id, license_plate, date, search_username
        )
    else:
        sessions = ParkingSessionService.get_user_sessions(
            db, username, limit, parking_lot_id, license_plate, date, search_username
        )

    return sessions
