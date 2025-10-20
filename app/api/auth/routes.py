from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User
from datetime import datetime, date
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: EmailStr
    phone: str
    birth_year: int

    role: str = "user"
    active: bool = True

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    role: str
    created_at: date
    birth_year: int
    active: bool

router = APIRouter(prefix="/auth", tags=["Authorization"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# http://127.0.0.1:8000/auth/
@router.get("/")
async def root(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(db: Session = Depends(get_db), user: UserCreate):
    """
    registers a new user
    """

    # Checks for user validation
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Checks for email validation
    db_email = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    """
    ToDo - HASHING PASSWORD HERE !!!!
    """

    # This makes the User Object to be returned
    db_user = UserDB(
        username=user.username,
        password=hashed_password,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        created_at=date.today(),
        birth_year=user.birth_year,
        active=user.active
    )       

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
