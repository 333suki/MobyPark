from pydantic import BaseModel
from typing import Optional

# DTO's, these go in the request body
class ProfileUpdateBody(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None
