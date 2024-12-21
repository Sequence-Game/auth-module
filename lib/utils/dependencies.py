from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.config import settings
from lib.models import Base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
