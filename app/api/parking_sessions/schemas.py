from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParkingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parking_lot_id: int
    license_plate: str
    started: datetime
    stopped: Optional[datetime]
    username: str
    duration_minutes: Optional[int]
    cost: Optional[float]
    payment_status: str


# class StartParkingSessionBody(BaseModel):
#     start_time: Optional[datetime]


class StopParkingSessionBody(BaseModel):
    discount_code: Optional[str] = None
