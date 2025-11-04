from pydantic import BaseModel
from datetime import date

class RegisterBody(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: int

    role: str = "user"
    active: bool = True

# class RegisterResponse(BaseModel):
#     id: int
#     username: str
#     name: str
#     email: str
#     phone: str
#     role: str
#     created_at: date
#     birth_year: int
#     active: bool

    # class Config: # USE THIS FOR SQLAlchemy MODELS!
    #     from_attributes = True

class LoginBody(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    role: str
    created_at: date
    birth_year: int
    active: bool
    token: str

    class Config: # USE THIS FOR SQLAlchemy MODELS!
        from_attributes = True

class LogoutBody(BaseModel):
    token: str
