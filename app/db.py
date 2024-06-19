from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

database_url = settings.database_url
metadata = MetaData()
Base = declarative_base()

def engine_factory(database_url, **kwargs):
    if not kwargs:
        return create_engine(database_url, pool_pre_ping=True)
    else:
        return create_engine(database_url, **kwargs)

def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_factory(database_url))
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()