from pydantic import BaseModel, Field
from typing import Optional


class VehicleBase(BaseModel):
    license_plate: str
    make: str
    model: str
    color: str
    year: str


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    """All fields are optional for partial updates"""
    license_plate: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None


class VehicleResponse(VehicleBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True