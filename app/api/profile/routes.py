from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from sqlalchemy.orm import Session

from app.api.profile.schemas import UpdateProfileBody
from app.db.database import SessionLocal
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError

from app.db.models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/", status_code=status.HTTP_200_OK)
async def update_profile(request: Request, body: Optional[UpdateProfileBody] = Body(None), db: Session = Depends(get_db)):
    """
    Update Profile
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

    # Check if there is no body provided
    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body"
        )
    
    # Check if the body is empty
    if all(value is None for value in body.dict().values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body"
        )
    
    user_id: int = user_info.get("sub")
    user_role: str = user_info.get("role")

    user: User | None = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Username validation check and update
    if body.username is not None:
        if db.query(User).filter(User.username == body.username).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        else:
            user.username = body.username

    # Password update
    if body.password is not None:
        user.password = body.passowrd

    # Name update
    if body.name is not None:
        user.name = body.name

    # Email validation and update
    if body.email is not None:
        if db.query(User).filter(User.email == body.email).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        else:
            user.email = body.email

    # phone validation check and update
    if body.phone is not None:
        if db.query(User).filter(User.phone == body.phone).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already taken"
            )
        else:
            user.phone = body.phone

    # Birthyear update
    if body.birth_year is not None:
            user.birth_year = body.birth_year

    db.commit()
    return { "message": "Profile Updated successfully" }
