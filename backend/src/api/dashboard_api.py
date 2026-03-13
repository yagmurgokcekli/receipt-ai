from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.user_info import UserInfo
from src.core.auth import is_authorized

from src.logic import dashboard_logic


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)


@router.get("/category-distribution")
def get_category_distribution(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return dashboard_logic.get_category_distribution(
        db=db,
        user_info=user_info,
    )


@router.get("/monthly-trend")
def get_monthly_trend(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return dashboard_logic.get_monthly_trend(
        db=db,
        user_info=user_info,
    )


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return dashboard_logic.get_summary(
        db=db,
        user_info=user_info,
    )  