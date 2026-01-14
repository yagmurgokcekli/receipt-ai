from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.settings import settings
import src.db.models


DATABASE_URL = (
    "mssql+pyodbc://"
    f"{settings.AZURE_SQL_USERNAME}:{settings.AZURE_SQL_PASSWORD}"
    f"@{settings.AZURE_SQL_SERVER}:1433/"
    f"{settings.AZURE_SQL_DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
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
