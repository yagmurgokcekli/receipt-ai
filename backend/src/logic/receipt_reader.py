from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.db.repositories.receipt_repository import (
    get_all_receipts,
    get_receipt_by_id,
    get_receipts_by_source,
)
from src.schemas.receipt import ReceiptSchema


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
