from pydantic import BaseModel, EmailStr, Field

class RegisterUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginUser(BaseModel):
    email: EmailStr
    password: str
