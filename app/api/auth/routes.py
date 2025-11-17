from datetime import date

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.auth.schemas import RegisterBody, LoginBody, LoginResponse, LogoutBody
from app.db.database import SessionLocal
from app.db.models.user import User
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.api.login_sessions.session_manager import LoginSessionManager
from app.api.auth.schemas import RegisterBody, LoginBody, LoginResponse, LogoutBody
from pydantic import BaseModel
from datetime import date
from app.util import auth_utils
import bcrypt
import uuid
import re



router = APIRouter(prefix="/auth", tags=["Authorization"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

    # Checks for email uniqueness and validates email format
    db_email = db.query(User).filter(User.email == body.email).first()
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = auth_utils.hash_password(body.password)

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

    return { "message": "Registered successfully" }

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login_user(body: LoginBody, db: Session = Depends(get_db)):
    """
    Logs in a user
    """

    # Checks if the user exists
    user: User | None = db.query(User).filter(User.username == body.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username doesn't exist"
        )

    # Checks if the password is correct
    if not bcrypt.checkpw(body.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

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

@router.post("/logout", response_model=LoginResponse)
async def logout_user(request: Request, body: LogoutBody):
    """
    Logs a user out
    """
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenInvalidError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    return Response(status_code=204)
