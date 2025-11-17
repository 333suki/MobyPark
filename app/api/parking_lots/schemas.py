from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ParkingLotsResponse(BaseModel):
    id: int
    name: str
    location: str
    address: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: int
    created_at: datetime
    coordinates_lat: float
    coordinates_lng: float

    class Config:
        from_attributes = True

class CreateParkingLotBody(BaseModel):
    name: str
    location: str
    address: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: int
    coordinates_lat: float
    coordinates_lng: float

class UpdateParkingLotBody(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    reserved: Optional[int] = None
    tariff: Optional[float] = None
    daytariff: Optional[int] = None
    coordinates_lat: Optional[float] = None
    coordinates_lng: Optional[float] = None
