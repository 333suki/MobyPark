from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    transaction: str
    amount: float


class PaymentRefund(BaseModel):
    amount: float
    transaction: Optional[str] = None
    coupled_to: Optional[str] = None


class TransactionBody(BaseModel):
    id: int
    amount: float
    method: str
    issuer: str
    bank: str

class PaymentComplete(BaseModel):
    t_data: TransactionBody
    validation: str