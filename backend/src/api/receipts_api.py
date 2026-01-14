from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from typing import Union, List

from src.logic.receipt_processor import process_receipt
from src.logic.receipt_reader import (
    read_all_receipts,
    read_receipt_by_id,
    read_receipts_by_source,
)

from src.schemas.receipt import ReceiptSchema
from src.schemas.receipt_response import ReceiptAnalysisResponse
from src.schemas.receipt_compare_response import ReceiptCompareResponse
from src.schemas.engine import Engine

from sqlalchemy.orm import Session
from src.db.session import get_db


router = APIRouter(tags=["receipts"])


@router.post("", response_model=Union[ReceiptAnalysisResponse, ReceiptCompareResponse])
async def handle_receipt(
    file: UploadFile = File(...),
    method: Engine = Query(default=Engine.di),
    db: Session = Depends(get_db),
):
    """
    Handle receipt upload and trigger processing using the selected extraction engine.

    The file is uploaded by the client, validated, and then passed to the business
    logic layer for storage and receipt analysis.

    Args:
        file (UploadFile):
            Receipt image uploaded by the client.
        method (Engine, optional):
            Processing engine to use. Defaults to "di".
            Supported values: "di", "openai", "compare".

    Returns:
        dict: Processed receipt result returned from the logic layer.

    Raises:
        HTTPException: Raised when the uploaded file is missing or invalid.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    return await process_receipt(file, method.value, db)


@router.get(
    "",
    response_model=List[ReceiptSchema],
)
def list_receipts(
    source: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    List receipts. Optionally filter by source.
    """
    if source:
        return read_receipts_by_source(source, db)

    return read_all_receipts(db)


@router.get(
    "/{receipt_id}",
    response_model=ReceiptSchema,
)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single receipt by ID.
    """
    return read_receipt_by_id(receipt_id, db)
