from fastapi import APIRouter, UploadFile, File, Query, Depends
from typing import Union, List
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.receipt import (
    ReceiptDetailSchema,
    ReceiptSchema,
    ReceiptAnalysisResponse,
    ReceiptCompareResponse,
    ReceiptListSchema,
)
from src.schemas.engine import Engine
from src.schemas.user_info import UserInfo
from src.core.auth import is_authorized

from src.logic import receipt_logic


router = APIRouter(
    tags=["receipts"],
)


@router.post("", response_model=Union[ReceiptAnalysisResponse, ReceiptCompareResponse])
async def handle_receipt(
    file: UploadFile = File(...),
    method: Engine = Query(default=Engine.di),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):

    return await receipt_logic.handle_receipt_logic(
        file=file,
        method=method,
        db=db,
        user_info=user_info,
    )


@router.get("", response_model=List[ReceiptListSchema])
def list_receipts(
    source: Engine | None = Query(default=None),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return receipt_logic.list_receipts_logic(
        db=db,
        user_info=user_info,
        source=source,
    )


@router.get("/{receipt_id}", response_model=ReceiptDetailSchema)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return receipt_logic.get_receipt_logic(
        db=db,
        user_info=user_info,
        receipt_id=receipt_id,
    )


@router.put("/{receipt_id}", response_model=ReceiptSchema)
def update_receipt_endpoint(
    receipt_id: int,
    updated_data: ReceiptSchema,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return receipt_logic.update_receipt_logic(
        db=db,
        user_info=user_info,
        receipt_id=receipt_id,
        updated_data=updated_data,
    )


@router.delete("/{receipt_id}")
def delete_receipt_endpoint(
    receipt_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(is_authorized),
):
    return receipt_logic.delete_receipt_logic(
        db=db,
        user_info=user_info,
        receipt_id=receipt_id,
    )
