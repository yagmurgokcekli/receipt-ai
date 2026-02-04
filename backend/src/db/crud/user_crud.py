from sqlalchemy.orm import Session
from src.db.models.user import User
from src.schemas.user import UserCreate
from src.core.security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_pw = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
