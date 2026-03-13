from sqlalchemy.orm import Session

from src.schemas.user_info import UserInfo
from src.db.crud.user_crud import get_or_create_user


def resolve_user(
    db: Session,
    user_info: UserInfo,
):
    """
    Resolve application user from Microsoft token.
    Creates the user in DB if it does not exist.
    """

    return get_or_create_user(
        db=db,
        oid=user_info.user_id,
        email=user_info.email,
        name=user_info.name,
    )
