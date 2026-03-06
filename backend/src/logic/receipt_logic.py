from fastapi import UploadFile, HTTPException
from typing import Union
from sqlalchemy.orm import Session

from src.schemas.engine import Engine
from src.schemas.user_info import UserInfo
from src.schemas.receipt import (
    ReceiptSchema,
    ReceiptAnalysisResponse,
    ReceiptCompareResponse,
)

from src.db.crud.receipt_crud import (
    get_receipts_by_user,
    get_receipts_by_user_and_source,
    read_receipt_by_id_for_user,
    update_receipt,
    delete_receipt,
)

from src.logic.receipt_processor import process_receipt
from src.logic.user_resolver import resolve_user


async def handle_receipt_logic(
    file: UploadFile,
    method: Engine,
    db: Session,
    user_info: UserInfo,
) -> Union[ReceiptAnalysisResponse, ReceiptCompareResponse]:

    if not file.filename or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="File has no name")

    user = resolve_user(db, user_info)

    return await process_receipt(
        file,
        method,
        db,
        user.id,
    )


def list_receipts_logic(
    db: Session,
    user_info: UserInfo,
    source: Engine | None,
):

    user = resolve_user(db, user_info)

    if source:
        return get_receipts_by_user_and_source(
            db,
            user.id,
            source.value,
        )

    return get_receipts_by_user(db, user.id)


def get_receipt_logic(
    db: Session,
    user_info: UserInfo,
    receipt_id: int,
):

    user = resolve_user(db, user_info)

    return read_receipt_by_id_for_user(
        db,
        receipt_id,
        user.id,
    )


def update_receipt_logic(
    db: Session,
    user_info: UserInfo,
    receipt_id: int,
    updated_data: ReceiptSchema,
):

    user = resolve_user(db, user_info)

    return update_receipt(
        db,
        receipt_id,
        user.id,
        updated_data,
    )


def delete_receipt_logic(
    db: Session,
    user_info: UserInfo,
    receipt_id: int,
):

    user = resolve_user(db, user_info)

    delete_receipt(
        db,
        receipt_id,
        user.id,
    )

    return {"message": "Receipt deleted successfully"}
