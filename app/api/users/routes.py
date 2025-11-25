from http.client import HTTPException
from fastapi import APIRouter, Response, Request, Query, HTTPException, status
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.users.schemas import UpdateUserBody, UserResponse
from app.db.database import SessionLocal
from app.db.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@router.get("/users", response_model=list[UserResponse])
async def root(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    return UserResponse(
        id = db_user.id,
        username = db_user.username,
        name = db_user.name,
        email = db_user.email,
        phone = db_user.phone,
        birth_year = db_user.birth_year,
        role = db_user.role,
        active = db_user.active,
        created_at = db_user.created_at
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserResponse, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        name=user.name,
        email=user.email,
        phone=user.phone,
        birth_year=user.birth_year,
        role=user.role,
        active=user.active,
        created_at=user.created_at
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return { "message": "User created successfully" }

@router.put("/{user_id}",  status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UpdateUserBody, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    db_user.username = user.username
    db_user.name = user.name
    db_user.email = user.email
    db_user.phone = user.phone
    db_user.birth_year = user.birth_year
    db_user.role = user.role
    db_user.active = user.active
    db.commit()
    db.refresh(db_user)
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    db.delete(db_user)
    db.commit()
    return Response(status_code=200)