from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.user import User
from app.api.login_sessions.session_manager import LoginSessionManager
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
    """
    Hash a password using bcrypt
    """

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

class RegisterBody(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: int

    role: str = "user"
    active: bool = True

# class RegisterResponse(BaseModel):
#     id: int
#     username: str
#     name: str
#     email: str
#     phone: str
#     role: str
#     created_at: date
#     birth_year: int
#     active: bool

    class Config: # USE THIS FOR SQLAlchemy MODELS!
        from_attributes = True

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, body: RegisterBody, db: Session = Depends(get_db), ):
    """
    Registers a new user
    """

    # Checks for user uniqueness
    db_user = db.query(User).filter(User.username == body.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Checks for email uniqueness
    db_email = db.query(User).filter(User.email == body.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    """
    ToDo - HASHING PASSWORD HERE !!!!
    """
    hashed_password = hash_password(body.password)

    # This makes the User Object to be returned
    db_user = User(
        username=body.username,
        password=hashed_password,
        name=body.name,
        email=body.email,
        phone=body.phone,
        role=body.role,
        created_at=date.today(),
        birth_year=body.birth_year,
        active=body.active
    )       

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return { "message": "Registered successfully" }

class LoginBody(BaseModel):
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
async def login_user(body: LoginBody, db: Session = Depends(get_db), ):
    """
    Logs in a user
    """

    # Checks if the user exists
    db_user = db.query(User).filter(User.username == body.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username doesn't exist"
        )

    # Check if user is already logged in
    if db_user.id in LoginSessionManager.sessions.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already logged in"
        )

    # Checks if the password is correct
    if not bcrypt.checkpw(body.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = str(uuid.uuid4())

    # Add the login session to the session manager
    LoginSessionManager.add_session(token, db_user.id)

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

class LogoutBody(BaseModel):
    token: str

@router.post("/logout", response_model=LoginResponse)
async def logout_user(request: Request, body: LogoutBody):
    """
    Logs a user out
    """

    if not LoginSessionManager.remove_session(body.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session token"
        )

    return Response(status_code=204)
