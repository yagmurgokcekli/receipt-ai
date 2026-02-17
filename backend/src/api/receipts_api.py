from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from typing import Union, List
from sqlalchemy.orm import Session
from src.logic.receipt_processor import process_receipt
from src.db.crud.receipt_crud import (
    read_all_receipts,
    read_receipt_by_id,
    read_receipts_by_source,
)
from src.db.crud.user_crud import get_or_create_user
from src.db.session import get_db
from src.schemas.receipt import (
    ReceiptSchema,
    ReceiptAnalysisResponse,
    ReceiptCompareResponse,
)
from src.schemas.engine import Engine
from src.schemas.user_info import UserInfo
from src.core.auth import is_authorized


router = APIRouter(tags=["receipts"])

@router.post("", response_model=Union[ReceiptAnalysisResponse, ReceiptCompareResponse])
async def handle_receipt(
    file: UploadFile = File(...),
    method: Engine = Query(default=Engine.di),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    user = get_or_create_user(
        db,
        oid=user_info.user_id,
        email=user_info.email,
        name=user_info.name,
    )

    return await process_receipt(
        file,
        method.value,
        db,
        user.id,
    )


@router.get("", response_model=List[ReceiptSchema])
def list_receipts(
    source: Engine | None = Query(default=None),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    if source:
        return read_receipts_by_source(source.value, db)

    return read_all_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptSchema)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return read_receipt_by_id(receipt_id, db)

