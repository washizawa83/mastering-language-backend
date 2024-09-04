from sqlalchemy import Column, Integer
from sqlalchemy_utils import EmailType

from api.db import Base

class Verification(Base):
    __tablename__ = 'verifications'

    email = Column(EmailType, primary_key=True, unique=True)
    verification_code = Column(Integer)