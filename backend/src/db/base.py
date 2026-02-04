from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    All SQLAlchemy models must inherit from this Base
    so that Alembic can correctly detect metadata changes.
    """

    pass
