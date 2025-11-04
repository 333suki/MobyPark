from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Optional

from app.api.profile.schemas import ProfileUpdateBody

router = APIRouter(prefix="/profile", tags=["Profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def root():
    return {"message": "Hello Profiles!"}

@router.put("/update", status_code=status.HTTP_200_OK)
async def update_profile(request: Request, body: Optional[ProfileUpdateBody] = Body(None), db: Session = Depends(get_db)):
    """
    Update Profile
    """

    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "No Authorization header provided"
        )

    return { "message": "Profile Updated successfully" }
