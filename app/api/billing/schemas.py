from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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
    session: SessionInfo
    parking: ParkingInfo
    amount: float
    thash: str
    payed: float
    balance: float
    
    class Config:
        from_attributes = True