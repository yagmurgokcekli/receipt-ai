from sqlalchemy.orm import DeclarativeBase
import src.db.models


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    All SQLAlchemy models must inherit from this Base
    so that Alembic can correctly detect metadata changes.
    """

    pass
