from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.parking_lot import ParkingLot

class DbUtils:
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
    def get_parking_lot_by_id(db: Session, parking_lot_id: int) -> ParkingLot | None:
        parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
        if not parking_lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parking lot not found"
            )
        return parking_lot
    
    @staticmethod
    def get_username(db: Session, user_id: int) -> str | None:
        """Get username by user ID"""
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else None