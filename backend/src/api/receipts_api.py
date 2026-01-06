from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from enum import Enum
from src.logic.receipt_processor import process_receipt


class Engine(str, Enum):
    di = "di"
    openai = "openai"


router = APIRouter(tags=["receipts"])


@router.post("")
async def handle_receipt(
    file: UploadFile = File(...), method: Engine = Query(default="di")
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
            Supported values: "di", "openai".

    Returns:
        dict: Processed receipt result returned from the logic layer.

    Raises:
        HTTPException: Raised when the uploaded file is missing or invalid.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    return await process_receipt(file, method.value)
