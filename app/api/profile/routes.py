from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
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
    username: str | None
    password: str | None
    name: str | None
    email: str | None
    phone: str | None
    birth_year: int | None

@router.get("/")
async def root():
    return {"message": "Hello Profiles!"}

@router.put("/update", status_code=status.HTTP_200_OK)
async def update_profile(request: Request, body: ProfileUpdateBody, db: Session = Depends(get_db)):
    """
    Update Profile
    """

    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "No Authorization header provided"
        )