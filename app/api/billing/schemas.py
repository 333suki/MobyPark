from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionInfo(BaseModel):
    license_plate: str
    started: datetime
    stopped: Optional[datetime]
    hours: float
    days: int


class ParkingInfo(BaseModel):
    name: str
    location: str
    tariff: float
    daytariff: float


class BillingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session: SessionInfo
    parking: ParkingInfo
    amount: float
    thash: str
    payed: float
    balance: float
