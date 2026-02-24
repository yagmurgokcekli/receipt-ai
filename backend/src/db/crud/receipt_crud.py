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


def read_receipt_by_id_for_user(
    db: Session,
    receipt_id: int,
    user_id: int,
) -> ReceiptSchema:
    """
    Return a single receipt by ID if it belongs to the user.
    """

    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == user_id,
        )
        .first()
    )

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail=f"Receipt with id={receipt_id} not found",
        )

    return ReceiptSchema.model_validate(receipt)


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


def update_receipt(
    db: Session,
    receipt_id: int,
    user_id: int,
    updated_data: ReceiptSchema,
) -> Receipt:
    """
    Update a receipt if it belongs to the user.
    """

    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_id, Receipt.user_id == user_id)
        .first()
    )

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail=f"Receipt with id={receipt_id} not found",
        )

    receipt.merchant = updated_data.merchant
    receipt.total = updated_data.total
    receipt.currency = updated_data.currency
    receipt.transaction_date = updated_data.transaction_date
    receipt.source = updated_data.source

    receipt.items.clear()

    if updated_data.items:
        for item in updated_data.items:
            receipt.items.append(
                ReceiptItem(
                    name=item.name,
                    quantity=item.quantity,
                    price=item.price,
                )
            )

    db.commit()
    db.refresh(receipt)

    return receipt


def delete_receipt(
    db: Session,
    receipt_id: int,
    user_id: int,
) -> None:
    """
    Delete a receipt if it belongs to the user.
    """

    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_id, Receipt.user_id == user_id)
        .first()
    )

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail=f"Receipt with id={receipt_id} not found",
        )

    db.delete(receipt)
    db.commit()
