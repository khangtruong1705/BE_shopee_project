from sqlmodel import Session, create_engine


from app.core.config import settings


def get_session():
    with Session(engine) as session:
        yield session


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


print('database',settings.SQLALCHEMY_DATABASE_URI)
