from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str


class User(BaseUser):
    id: str
    email: str
    password: str
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(BaseUser):
    email: str
    password: str


class UserResponse(BaseUser):
    pass
