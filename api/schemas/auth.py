from pydantic import BaseModel, EmailStr


class Verification(BaseModel):
    email: str
    verification_code: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str | None = None


class EmailPasswordRequestForm(BaseModel):
    email: EmailStr
    password: str


class LoginAndVerifyForm(Verification):
    password: str


class SignupRequestForm(BaseModel):
    username: str
    email: EmailStr
    password: str
