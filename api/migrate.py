from sqlalchemy import create_engine

from api.models.user import Base as user_base
from api.models.auth import Base as auth_base
from api.models.deck import Base as deck_base


DB_URL = 'mysql+pymysql://root@db:3306/app?charset=utf8'
engine = create_engine(DB_URL, echo=True)


def reset_database():
    user_base.metadata.drop_all(bind=engine)
    auth_base.metadata.drop_all(bind=engine)
    deck_base.metadata.drop_all(bind=engine)

    user_base.metadata.create_all(bind=engine)
    auth_base.metadata.create_all(bind=engine)
    deck_base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
