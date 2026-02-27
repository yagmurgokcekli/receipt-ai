from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from src.db.session import get_db
from src.db.models.receipt import Receipt, ReceiptItem
from src.db.crud.user_crud import get_or_create_user
from src.schemas.user_info import UserInfo
from src.core.auth import is_authorized

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/category-distribution")
def get_category_distribution(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    user = get_or_create_user(
        db,
        oid=user_info.user_id,
        email=user_info.email,
        name=user_info.name,
    )

    results = (
        db.query(
            ReceiptItem.category,
            func.sum(ReceiptItem.price).label("total"),
        )
        .join(Receipt)
        .filter(Receipt.user_id == user.id)
        .group_by(ReceiptItem.category)
        .all()
    )

    return [
        {"category": r[0] or "Uncategorized", "total": float(r[1] or 0)}
        for r in results
    ]


@router.get("/monthly-trend")
def get_monthly_trend(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    user = get_or_create_user(
        db,
        oid=user_info.user_id,
        email=user_info.email,
        name=user_info.name,
    )

    results = (
        db.query(
            func.year(Receipt.transaction_date).label("year"),
            func.month(Receipt.transaction_date).label("month"),
            func.sum(Receipt.total).label("total"),
        )
        .filter(Receipt.user_id == user.id)
        .group_by(
            func.year(Receipt.transaction_date),
            func.month(Receipt.transaction_date),
        )
        .order_by(
            func.year(Receipt.transaction_date),
            func.month(Receipt.transaction_date),
        )
        .all()
    )

    return [
        {
            "year": r[0],
            "month": r[1],
            "total": float(r[2] or 0),
        }
        for r in results
    ]


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    user = get_or_create_user(
        db,
        oid=user_info.user_id,
        email=user_info.email,
        name=user_info.name,
    )

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    # this month
    current_total = (
        db.query(func.sum(Receipt.total))
        .filter(
            Receipt.user_id == user.id,
            func.year(Receipt.transaction_date) == current_year,
            func.month(Receipt.transaction_date) == current_month,
        )
        .scalar()
        or 0
    )

    # previous month
    prev_month = current_month - 1 or 12
    prev_year = current_year if current_month != 1 else current_year - 1

    previous_total = (
        db.query(func.sum(Receipt.total))
        .filter(
            Receipt.user_id == user.id,
            func.year(Receipt.transaction_date) == prev_year,
            func.month(Receipt.transaction_date) == prev_month,
        )
        .scalar()
        or 0
    )

    percent_change = 0
    if previous_total > 0:
        percent_change = ((current_total - previous_total) / previous_total) * 100

    # top category
    top_category = (
        db.query(
            ReceiptItem.category,
            func.sum(ReceiptItem.price).label("total"),
        )
        .join(Receipt)
        .filter(
            Receipt.user_id == user.id,
            func.year(Receipt.transaction_date) == current_year,
            func.month(Receipt.transaction_date) == current_month,
        )
        .group_by(ReceiptItem.category)
        .order_by(func.sum(ReceiptItem.price).desc())
        .first()
    )

    return {
        "current_month_total": float(current_total),
        "previous_month_total": float(previous_total),
        "percent_change": round(percent_change, 2),
        "top_category": top_category[0] if top_category else None,
    }
