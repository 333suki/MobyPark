from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParkingLotsResponse(BaseModel):
    id: int
    name: str
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
