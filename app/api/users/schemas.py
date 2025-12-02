from datetime import date
from pydantic import BaseModel


class UserBody(BaseModel):
    id: int
    
class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    birth_year: int
    role: str
    active: bool
    created_at: date

    class Config:  # USE THIS FOR SQLAlchemy MODELS!
        from_attributes = True

class UpdateUserBody(BaseModel):
    username: str
    name: str
    email: str
    phone: str
    birth_year: int
    role: str
    active: bool