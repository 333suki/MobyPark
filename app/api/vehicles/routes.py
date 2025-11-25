from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.api.vehicles.schemas import VehicleResponse, VehicleCreate, VehicleUpdate
from app.db.models.vehicle import Vehicle

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

def get_db():
    "Gets database session"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_user_token(request: Request) -> int:
    """
    Validates JWT token and returns user_id
    Raises HTTPException if validation fails
    """
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

    try:
        user_id: int = int(user_info["sub"])
    except (ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token"
        )

    return user_id

# Adding a vehicle
# Users can add vehicles to their profile with a unique license plate and a name.
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VehicleResponse)
async def create_vehicle(
        request: Request,
        body: VehicleCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new vehicle for the authenticated user.
    License plate must be unique per user.
    """
    user_id = validate_user_token(request)

    # Check if vehicle with same license plate already exists for this user
    existing_vehicle = db.query(Vehicle).filter(
        Vehicle.license_plate == body.license_plate,
        Vehicle.user_id == user_id
    ).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this license plate already exists"
        )

    # Creates a new vehicle
    db_vehicle = Vehicle(
        license_plate=body.license_plate,
        make=body.make,
        model=body.model,
        color=body.color,
        year=body.year,
        user_id=user_id
    )

    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)

    return db_vehicle


# Updating a vehicle
# Users can update any field of their vehicle.
@router.put("/{license_plate}", response_model=VehicleResponse)
async def update_vehicle(
        license_plate: str,
        body: VehicleUpdate,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Update a vehicle's information.
    Users can update any field of their vehicle.
    """
    user_id = validate_user_token(request)

    # Get vehicle
    vehicle = db.query(Vehicle).filter(
        Vehicle.license_plate == license_plate,
        Vehicle.user_id == user_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    # Update fields if provided
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    return vehicle

# Deleting a vehicle
# Users can delete a vehicle from their profile.
@router.delete("/{license_plate}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
        license_plate: str,
        request: Request,
        db: Session = Depends(get_db)
):
    # Delete a vehicle from the user's profile.
    user_id = validate_user_token(request)

    # Get vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate,Vehicle.user_id == user_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    db.delete(vehicle)
    db.commit()
    db.refresh(vehicle)
    return None

# Viewing vehicles
# Users can view all their vehicles; admins can view vehicles for any user.
@router.get("/", response_model=List[VehicleResponse])
async def get_vehicles(
        request: Request,
        db: Session = Depends(get_db)
):

    # Get all vehicles for the authenticated user.
    user_id = validate_user_token(request)

    # Get all vehicles for this user
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == user_id).all()

    # Return all vehicles
    return vehicles


@router.get("/{license_plate}", response_model=VehicleResponse)
async def get_vehicle_by_license_plate(
        license_plate: str,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Get a specific vehicle by license plate for the authenticated user.
    """
    user_id = validate_user_token(request)

    # Get vehicle
    vehicle = db.query(Vehicle).filter(
        Vehicle.license_plate == license_plate,
        Vehicle.user_id == user_id
    ).first()

    # If vehicle not found, raise 404
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )

    return vehicle

