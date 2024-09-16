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
    class Config:
        orm_mode = True
        from_attributes = True


class BaseUserSettings(BaseModel):
    level_one: int
    level_two: int
    level_three: int
    level_four: int
    level_five: int
    level_six: int
    level_seven: int


class UserSettings(BaseUserSettings):
    id: str


class UserSettingsResponse(BaseUserSettings):
    pass
