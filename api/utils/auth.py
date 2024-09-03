from passlib.context import CryptContext


SECRET_KEY = "eb4d5384734016fd3075d010a4b4d95ebb0005df4c65633e3f9e6c86c430c470"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
