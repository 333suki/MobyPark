from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReservationCreate(BaseModel):
    user_id: Optional[int] = None
    parking_lot_id: int
    license_plate: str
    start_time: datetime
    end_time: datetime
    status: Optional[str] = None
    cost: Optional[float] = None

class ReservationUpdate(BaseModel):
    parking_lot_id: Optional[int] = None
    license_plate: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    cost: Optional[float] = None
