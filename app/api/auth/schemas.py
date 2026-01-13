from datetime import date

from pydantic import BaseModel, ConfigDict


class RegisterBody(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: int

class LoginBody(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str

class LogoutBody(BaseModel):
    token: str
