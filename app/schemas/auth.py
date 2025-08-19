from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_admin: bool
    is_verified: bool

class SignUpIn(BaseModel):
    email: EmailStr
    password: str
