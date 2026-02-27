from typing import Optional
from sqlalchemy.orm import Session
from src.db.models.user import User


def get_user_by_microsoft_id(
    db: Session,
    microsoft_id: str,
) -> Optional[User]:
    return db.query(User).filter(User.microsoft_id == microsoft_id).first()


def create_user(
    db: Session,
    oid: str,
    email: str,
    name: Optional[str],
) -> User:
    user = User(
        microsoft_id=oid,
        email=email,
        name=name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_user(
    db: Session,
    oid: str,
    email: str,
    name: Optional[str],
) -> User:
    user = get_user_by_microsoft_id(db, oid)

    if user:
        return user

    return create_user(db, oid, email, name)
