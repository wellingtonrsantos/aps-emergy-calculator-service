from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    mobile_number: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    surname: str
    mobile_number: str
