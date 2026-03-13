from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from src.schemas.user_info import UserInfo
from src.logic.user_resolver import resolve_user

from src.db.models.receipt import Receipt, ReceiptItem


def get_category_distribution(
    db: Session,
    user_info: UserInfo,
):
    """
    Returns total spending grouped by category.
    """

    user = resolve_user(db, user_info)

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
        {
            "category": r[0] or "Uncategorized",
            "total": float(r[1] or 0),
        }
        for r in results
    ]


def get_monthly_trend(
    db: Session,
    user_info: UserInfo,
):
    """
    Returns monthly spending trend for the user.
    """

    user = resolve_user(db, user_info)

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


def get_summary(
    db: Session,
    user_info: UserInfo,
):
    """
    Returns dashboard summary statistics.
    """

    user = resolve_user(db, user_info)

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    # Current month total
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

    # Previous month calculation
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

    # Top category this month
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
