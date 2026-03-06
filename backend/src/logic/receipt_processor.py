import os
import time
import uuid
import asyncio
import logging
from typing import Union
from sqlalchemy.orm import Session
from fastapi import UploadFile

from src.settings import settings

from src.db.crud.receipt_crud import save_receipt

from src.services.blob_storage_service import blob_storage
from src.services.document_intelligence_service import DocumentIntelligenceService
from src.services.openai_service import OpenAIVisionService

from src.logic.receipt_normalizer import normalize_di_receipt
from src.logic.receipt_compare import build_diff
from src.logic.receipt_extractor import ReceiptOpenAIProcessor
from src.logic.expense_classifier import ExpenseClassifier

from src.schemas.engine import Engine
from src.schemas.receipt import (
    ReceiptSchema,
    ReceiptAnalysisResponse,
    ReceiptCompareResponse,
    ReceiptCompareAnalysis,
)


logger = logging.getLogger(__name__)

di_service = DocumentIntelligenceService(
    endpoint=settings.AZURE_DI_ENDPOINT,
    api_key=settings.AZURE_DI_KEY,
)

oai_service = OpenAIVisionService(
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    deployment=settings.AZURE_OPENAI_DEPLOYMENT,
)

processor = ReceiptOpenAIProcessor(oai_service)
expense_classifier = ExpenseClassifier(oai_service)


async def enrich_items_with_categories(analysis: ReceiptSchema):
    if not analysis.items:
        return

    item_names = [item.name for item in analysis.items if item.name]

    category_map = await expense_classifier.classify_items(
        items=item_names,
        merchant=analysis.merchant,
    )

    for item in analysis.items:
        if item.name and item.name in category_map:
            item.category = category_map[item.name]


async def process_receipt(
    file: UploadFile,
    method: Engine,
    db: Session,
    user_id: int,
) -> Union[ReceiptAnalysisResponse, ReceiptCompareResponse]:

    file_bytes = await file.read()

    name, ext = os.path.splitext(file.filename or "receipt.jpg")
    new_name = f"{int(time.time())}_{uuid.uuid4().hex}{ext}"

    blob_url = blob_storage.upload_bytes(new_name, file_bytes)
    sas_url = blob_storage.generate_read_sas(new_name)

    if method == Engine.di:

        raw_result = await di_service.analyze_receipt(sas_url)
        analysis = normalize_di_receipt(raw_result)

        await enrich_items_with_categories(analysis)

        try:
            saved_receipt = save_receipt(db, analysis, user_id, sas_url)
        except Exception:
            logger.exception("Failed to persist receipt")
            raise

        return ReceiptAnalysisResponse(
            id=saved_receipt.id,
            file_saved_as=new_name,
            blob_url=blob_url,
            method="di",
            analysis=analysis,
        )

    elif method == Engine.openai:

        analysis = await processor.analyze_receipt(sas_url)

        await enrich_items_with_categories(analysis)

        try:
            saved_receipt = save_receipt(db, analysis, user_id, sas_url)
        except Exception:
            logger.exception("Failed to persist receipt")
            raise

        return ReceiptAnalysisResponse(
            id=saved_receipt.id,
            file_saved_as=new_name,
            blob_url=blob_url,
            method="openai",
            analysis=analysis,
        )

    elif method == Engine.compare:

        di_task = di_service.analyze_receipt(sas_url)
        oai_task = processor.analyze_receipt(sas_url)

        raw_di, oai_model = await asyncio.gather(di_task, oai_task)

        di_model = normalize_di_receipt(raw_di)

        diff = build_diff(di=di_model, openai=oai_model)

        return ReceiptCompareResponse(
            file_saved_as=new_name,
            blob_url=blob_url,
            method="compare",
            analysis=ReceiptCompareAnalysis(
                di=di_model,
                openai=oai_model,
                diff=diff,
            ),
        )

    else:
        raise ValueError(
            f"Unsupported receipt processing method: {method!r}. "
            "Supported methods are: 'di', 'openai', and 'compare'."
        )
