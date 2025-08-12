from sqlmodel import Session, create_engine


from app.core.config import settings

# Back-end-DB
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def get_session():
    with Session(engine) as session:
        yield session


# data-warehouse-DB
warehouse_engine = create_engine(str(settings.SQLALCHEMY_WAREHOUSE_DATABASE_URI))

def get_warehouse_session():
    with Session(warehouse_engine) as session:
        yield session



print('database',settings.SQLALCHEMY_DATABASE_URI)
print('warehouse_database',settings.SQLALCHEMY_WAREHOUSE_DATABASE_URI)
