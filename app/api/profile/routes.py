from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from sqlalchemy.orm import Session

from app.api.profile.schemas import UpdateProfileBody
from app.db.database import SessionLocal
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError

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

    # user_id: int = user_info.get("sub")
    # user_role: str = user_info.get("role")

    return { "message": "Profile Updated successfully" }
