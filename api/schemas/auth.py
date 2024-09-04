from pydantic import BaseModel


class Verification(BaseModel):
    email: str
    verification_code: int