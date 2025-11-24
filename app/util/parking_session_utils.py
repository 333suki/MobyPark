import math
from datetime import datetime
from typing import Optional, List

from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from app.db.models.parking_lot import ParkingLot
from app.db.models.parking_session import ParkingSession
from app.db.models.user import User
from app.db.models.vehicle import Vehicle


class ParkingSessionService:
    
    @staticmethod
    def check_active_session(db: Session, license_plate: str) -> bool:
        """Check if there's an active session for the given license plate"""
        active_session = db.query(ParkingSession).filter(
            ParkingSession.license_plate == license_plate,
            ParkingSession.stopped == None
        ).first()
        return active_session is not None

    @staticmethod
    def get_user_by_license_plate(db: Session, license_plate: str) -> Optional[User]:
        """Get user by license plate if it's registered to their account"""
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        if vehicle:
            return db.query(User).filter(User.id == vehicle.user_id).first()
        return None
    
    @staticmethod
    def get_username(db: Session, user_id: int) -> Optional[str]:
        """Get username by user ID"""
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else None
    
    @staticmethod
    def get_all_sessions(
        db: Session,
        limit: Optional[int] = None,
        parking_lot_id: Optional[int] = None,
        license_plate: Optional[str] = None,
        date: Optional[datetime] = None,
        search_username: Optional[str] = None
    ) -> List[ParkingSession]:
        """Get all parking sessions with optional filters (admin only)"""
        query = db.query(ParkingSession)
        
        # Apply filters
        if parking_lot_id is not None:
            query = query.filter(ParkingSession.parking_lot_id == parking_lot_id)
        
        if license_plate:
            query = query.filter(ParkingSession.license_plate.ilike(f"%{license_plate}%"))
        
        if search_username:
            query = query.filter(ParkingSession.username.ilike(f"%{search_username}%"))
        
        if date:
            # Filter by date (sessions that started or stopped on that date)
            query = query.filter(
                and_(
                    ParkingSession.started <= datetime.combine(date.date(), datetime.max.time()),
                    (ParkingSession.stopped == None) | 
                    (ParkingSession.stopped >= datetime.combine(date.date(), datetime.min.time()))
                )
            )
        
        # Order by most recent first
        query = query.order_by(desc(ParkingSession.started))
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_user_sessions(
        db: Session,
        username: str,
        limit: Optional[int] = None,
        parking_lot_id: Optional[int] = None,
        license_plate: Optional[str] = None,
        date: Optional[datetime] = None,
        search_username: Optional[str] = None
    ) -> List[ParkingSession]:
        """Get parking sessions for a specific user with optional filters"""
        # Start with username filter
        query = db.query(ParkingSession).filter(ParkingSession.username == username)
        
        # Apply other filters
        if parking_lot_id is not None:
            query = query.filter(ParkingSession.parking_lot_id == parking_lot_id)
        
        if license_plate:
            query = query.filter(ParkingSession.license_plate.ilike(f"%{license_plate}%"))
        
        # search_username is ignored for regular users (they can only see their own sessions)
        
        if date:
            # Filter by date (sessions that started or stopped on that date)
            query = query.filter(
                and_(
                    ParkingSession.started <= datetime.combine(date.date(), datetime.max.time()),
                    (ParkingSession.stopped == None) | 
                    (ParkingSession.stopped >= datetime.combine(date.date(), datetime.min.time()))
                )
            )
        
        # Order by most recent first
        query = query.order_by(desc(ParkingSession.started))
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def calculate_price(parking_lot: ParkingLot, session: ParkingSession) -> float:
        """Calculate the price for a parking session based on duration and parking lot rates"""
        price = 0
        start = session.started

        if session.stopped:
            end = session.stopped
        else:
            end = datetime.now()

        diff = end - start
        hours = math.ceil(diff.total_seconds() / 3600)

        if diff.total_seconds() < 180:
            price = 0
        elif end.date() > start.date():
            price = float(parking_lot.daytariff) * (diff.days + 1)
        else:
            price = float(parking_lot.tariff) * hours

            if price > float(parking_lot.daytariff):
                price = float(parking_lot.daytariff)

        return price
