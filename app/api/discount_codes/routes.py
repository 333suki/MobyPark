from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from sqlalchemy.orm import Session

from app.api.discount_codes.schemas import CreateDiscountCodeBody, DiscountCodeResponse, UpdateDiscountCodeBody
from app.db.database import SessionLocal
from app.db.models.discount_code import DiscountCode
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError

router = APIRouter(prefix="/discount_codes", tags=["discount_codes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DiscountCodeService:
    @staticmethod
    def get_all_discount_codes(
            db: Session,
            limit: Optional[int] = None,
            code: Optional[str] = None,
            percentage: Optional[int] = None,
            code_type: Optional[str] = None,
            used: Optional[bool] = None,
    ):
        query = db.query(DiscountCode)
        if code:
            query = query.filter(DiscountCode.code == code)
        if percentage:
            query = query.filter(DiscountCode.percentage == percentage)
        if code_type:
            query = query.filter(DiscountCode.type == code_type)
        if used:
            query = query.filter(DiscountCode.used == used)

        if limit:
            return query.order_by(DiscountCode.id).limit(limit).all()
        return query.order_by(DiscountCode.id).all()

@router.get("/", response_model=List[DiscountCodeResponse])
async def get_discount_codes(
        request: Request,
        limit: Optional[int] = Query(None, description="Limit the amount of results", ge=1),
        code: Optional[str] = Query(None, description="Filter by code"),
        percentage: Optional[int] = Query(None, description="Filter by discount percentage"),
        code_type: Optional[str] = Query(None, description="Filter by discount code type"),
        used: Optional[bool] = Query(None, description="Filter by discount code used status"),
        db: Session = Depends(get_db)
):
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

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    return DiscountCodeService.get_all_discount_codes(db, limit, code, percentage, code_type, used)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_discount_code(request: Request, body: Optional[CreateDiscountCodeBody] = Body(None), db: Session = Depends(get_db)):
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

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body provided"
        )

    if body.code is None or body.percentage is None or body.type is None or body.used is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing request fields"
        )

    # Make sure the code that is added is not already present
    if db.query(DiscountCode).filter(DiscountCode.code == body.code).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This code is already used"
        )

    discount_code: DiscountCode = DiscountCode(code=body.code, percentage=body.percentage, type=body.type, used=body.used)
    db.add(discount_code)
    db.commit()
    db.refresh(discount_code)
    return { "message": "Discount code created successfully" }

@router.put("/{discount_code_id}", status_code=status.HTTP_200_OK)
async def update_discount_code(discount_code_id: int, request: Request, body: Optional[UpdateDiscountCodeBody] = None, db: Session = Depends(get_db)):
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

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request body"
        )

    if body.code is None and body.percentage is None and body.type is None and body.used is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body"
        )

    discount_code: DiscountCode | None = db.query(DiscountCode).filter(DiscountCode.id == discount_code_id).first()

    if discount_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discount code with ID {discount_code_id} not found."
        )

    if body.code:
        discount_code.code = body.code
    if body.percentage:
        discount_code.percentage = body.percentage
    if body.type:
        discount_code.type = body.type
    if body.used:
        discount_code.used = body.used

    db.commit()
    db.refresh(discount_code)
    return {"message": "Discount code updated successfully"}

@router.delete("/{discount_code_id}", status_code=status.HTTP_200_OK)
async def delete_discount_code(discount_code_id: int, request: Request, db: Session = Depends(get_db)):
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

    role: str = user_info.get("role")

    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not admin"
        )

    if db.query(DiscountCode).filter(DiscountCode.id == discount_code_id).delete() == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discount code with ID {discount_code_id} not found."
        )

    db.commit()
    return {"message": "Discount code deleted successfully"}
