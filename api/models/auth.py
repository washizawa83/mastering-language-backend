from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils import EmailType

from api.db import Base

class Verification(Base):
    __tablename__ = 'verifications'

    email: Mapped[str] = mapped_column(EmailType, primary_key=True, unique=True)
    verification_code: Mapped[int] = mapped_column(Integer)