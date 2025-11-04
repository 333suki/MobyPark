from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.user import User

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
    def get_username(db: Session, user_id: int) -> str | None:
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else None
