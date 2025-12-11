from datetime import datetime
from pydantic import BaseModel


class ReservationCreate(BaseModel):
    parking_lot_id: int
    license_plate: str
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    cost: float

class ReservationUpdate(BaseModel):
    parking_lot_id: int
    license_plate: str
    start_time: datetime
    end_time: datetime
    status: str
    cost: float
