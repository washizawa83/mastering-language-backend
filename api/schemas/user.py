from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    email: str


class User(BaseUser):
    id: str
    password: str
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(BaseUser):
    password: str
