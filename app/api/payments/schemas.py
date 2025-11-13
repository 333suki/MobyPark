from typing import Optional

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    transaction: str
    amount: float


class PaymentRefund(BaseModel):
    amount: float
    transaction: Optional[str] = None
    coupled_to: Optional[str] = None


class PaymentComplete(BaseModel):
    t_data: dict
    validation: str