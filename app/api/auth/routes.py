from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User
from pydantic import BaseModel, EmailStr
import bcrypt
from datetime import date


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: str
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

    class Config: # USE THIS FOR SQLAlchemy MODELS!
        orm_mode = True

router = APIRouter(prefix="/auth", tags=["Authorization"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# http://127.0.0.1:8000/auth/
@router.get("/")
async def root(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user( user: UserCreate, db: Session = Depends(get_db),):
    """
    registers a new user
    """

    # Checks for user uniqueness
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Checks for email uniqueness
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    """
    ToDo - HASHING PASSWORD HERE !!!!
    """
    hashed_password = hash_password(user.password)

    # This makes the User Object to be returned
    db_user = User(
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
