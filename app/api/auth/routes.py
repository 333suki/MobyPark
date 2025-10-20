from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models.user import User
from pydantic import BaseModel
import bcrypt
from datetime import date
import uuid


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

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: int

    role: str = "user"
    active: bool = True

class RegisterResponse(BaseModel):
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
        from_attributes = True

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db), ):
    """
    registers a new user
    """

    # Checks for user uniqueness
    db_user = db.query(User).filter(User.username == request.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Checks for email uniqueness
    db_email = db.query(User).filter(User.email == request.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    """
    ToDo - HASHING PASSWORD HERE !!!!
    """
    hashed_password = hash_password(request.password)

    # This makes the User Object to be returned
    db_user = User(
        username=request.username,
        password=hashed_password,
        name=request.name,
        email=request.email,
        phone=request.phone,
        role=request.role,
        created_at=date.today(),
        birth_year=request.birth_year,
        active=request.active
    )       

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    role: str
    created_at: date
    birth_year: int
    active: bool
    token: str

    class Config: # USE THIS FOR SQLAlchemy MODELS!
        from_attributes = True

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login_user(request: LoginRequest, db: Session = Depends(get_db), ):
    """
    logs in a user
    """

    # Checks if a user exists
    db_user = db.query(User).filter(User.username == request.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username doesn't exist"
        )

    if not bcrypt.checkpw(request.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = str(uuid.uuid4())
    return LoginResponse(
        id=db_user.id,
        username=db_user.username,
        name=db_user.name,
        email=db_user.email,
        phone=db_user.phone,
        role=db_user.role,
        created_at=db_user.created_at,
        birth_year=db_user.birth_year,
        active=db_user.active,
        token=token
    )
