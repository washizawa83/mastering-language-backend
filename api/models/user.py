import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy_utils import UUIDType, EmailType

from api.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    username = Column(String(1024))
    email = Column(EmailType, unique=True)
    password = Column(String(1024))
    is_active = Column(Boolean, default=False)
