from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.crud.user_crud import create_user, get_user_by_email

from src.schemas.user import UserCreate, UserResponse
from src.schemas.user import UserLogin, TokenResponse

from src.core.security import verify_password, create_access_token

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = create_user(db, user_data)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, form_data.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }
