from datetime import date

from pydantic import BaseModel


class RegisterBody(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: int
    role: str = "user"
    active: bool = True

class LoginBody(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str

    class Config: # USE THIS FOR SQLAlchemy MODELS!
        from_attributes = True

class LogoutBody(BaseModel):
    token: str
