
from typing import Optional

from pydantic import BaseModel


class DiscountCodeResponse(BaseModel):
    id: int
    code: str
    percentage: int
    type: str
    used: bool

class CreateDiscountCodeBody(BaseModel):
    code: Optional[str] = None
    percentage: Optional[int] = None
    type: Optional[str] = None
    used: Optional[bool] = None

class UpdateDiscountCodeBody(BaseModel):
    code: Optional[str] = None
    percentage: Optional[int] = None
    type: Optional[str] = None
    used: Optional[bool] = None
