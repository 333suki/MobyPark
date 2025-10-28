from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import bcrypt

router = APIRouter(prefix="/profile", tags=["Profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DTO's, these go in the request body
class ProfileUpdateBody(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None

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
    return {"message": "Profile Updated successfully"}