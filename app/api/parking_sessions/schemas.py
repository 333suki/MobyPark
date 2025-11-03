from fastapi import Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParkingSessionResponse(BaseModel):
    id: int
    parking_lot_id: int
    license_plate: str
    started: datetime
    stopped: Optional[datetime]
    username: str
    duration_minutes: Optional[int]
    cost: Optional[float]
    payment_status: str

    class Config:
        from_attributes = True
