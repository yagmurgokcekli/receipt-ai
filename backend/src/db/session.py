from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.settings import settings


engine = create_engine(
    settings.DATABASE_URL, # type: ignore
    echo=False,
    future=True,
    pool_pre_ping=True,  
    pool_recycle=1800,  
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
