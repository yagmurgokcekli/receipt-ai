from sqlalchemy.orm import Session
from typing import List, Optional
from src.db.models.receipt import Receipt, ReceiptItem
from src.schemas.receipt import ReceiptSchema
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.schemas.engine import Engine
from src.schemas.receipt import ReceiptSchema


def save_receipt(
    db: Session,
    receipt_data: ReceiptSchema,
    user_id: int,
) -> Receipt:
    """
    Persist a normalized receipt and its items into the database.
    """

    receipt = Receipt(
        merchant=receipt_data.merchant,
        total=receipt_data.total,
        currency=receipt_data.currency,
        transaction_date=receipt_data.transaction_date,
        source=receipt_data.source,
        user_id=user_id,
    )

    if receipt_data.items:
        for item in receipt_data.items:
            receipt.items.append(
                ReceiptItem(
                    name=item.name,
                    quantity=item.quantity,
                    price=item.price,
                )
            )

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    return receipt


def get_all_receipts(db: Session) -> List[Receipt]:
    """
    Return all receipts ordered by newest first.
    """
    return db.query(Receipt).order_by(Receipt.created_at.desc()).all()


def get_receipt_by_id(
    db: Session,
    receipt_id: int,
) -> Optional[Receipt]:
    """
    Return a single receipt by its ID.
    """
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()


def get_receipts_by_source(
    db: Session,
    source: str,
) -> List[Receipt]:
    """
    Return receipts filtered by source (di / openai).
    """
    return (
        db.query(Receipt)
        .filter(Receipt.source == source)
        .order_by(Receipt.created_at.desc())
        .all()
    )


def read_all_receipts(db: Session) -> List[ReceiptSchema]:
    """
    Return all receipts from the database.
    """
    receipts = get_all_receipts(db)

    return [ReceiptSchema.model_validate(r) for r in receipts]


def read_receipt_by_id(
    receipt_id: int,
    db: Session,
) -> ReceiptSchema:
    """
    Return a single receipt by ID or raise 404.
    """
    receipt = get_receipt_by_id(db, receipt_id)

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail=f"Receipt with id={receipt_id} not found",
        )

    return ReceiptSchema.model_validate(receipt)


def read_receipts_by_source(
    source: str,
    db: Session,
) -> List[ReceiptSchema]:
    """
    Return receipts filtered by source.
    """
    receipts = get_receipts_by_source(db, source)

    return [ReceiptSchema.model_validate(r) for r in receipts]


def get_receipts_by_user(
    db: Session,
    user_id: int,
) -> List[Receipt]:
    return (
        db.query(Receipt)
        .filter(Receipt.user_id == user_id)
        .order_by(Receipt.created_at.desc())
        .all()
    )


def read_receipts_by_user(
    db: Session,
    user_id: int,
) -> List[ReceiptSchema]:
    receipts = get_receipts_by_user(db, user_id)
    return [ReceiptSchema.model_validate(r) for r in receipts]


def get_receipts_by_user_and_source(
    db: Session,
    user_id: int,
    source: str,
) -> List[Receipt]:
    return (
        db.query(Receipt)
        .filter(
            Receipt.user_id == user_id,
            Receipt.source == source,
        )
        .order_by(Receipt.created_at.desc())
        .all()
    )


def read_receipts_by_user_and_source(
    db: Session,
    user_id: int,
    source: str,
) -> List[ReceiptSchema]:
    receipts = get_receipts_by_user_and_source(db, user_id, source)
    return [ReceiptSchema.model_validate(r) for r in receipts]
