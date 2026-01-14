import os
import time
import uuid
import asyncio
from typing import Union

from src.db.repositories.receipt_repository import save_receipt
from src.schemas.receipt import ReceiptSchema
from src.settings import settings

from src.services.blob_storage_service import blob_storage
from src.services.document_intelligence_service import DocumentIntelligenceService
from src.services.openai_service import OpenAIVisionService

from src.logic.receipt_openai_processor import ReceiptOpenAIProcessor

from src.logic.normalizers.di_normalizer import normalize_di_receipt

from src.schemas.receipt_response import ReceiptAnalysisResponse
from src.schemas.receipt_compare_response import (
    ReceiptCompareResponse,
    ReceiptCompareAnalysis,
)

from src.utils.receipt_diff import build_diff

from sqlalchemy.orm import Session


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


async def process_receipt(
    file,
    method: str,
    db: Session,
) -> Union[ReceiptAnalysisResponse, ReceiptCompareResponse]:
    """
    Orchestrates the full receipt-processing workflow.

    This function acts as the application-level coordinator. It does not
    perform low-level logic itself, but delegates responsibilities to
    reusable infrastructure and domain services.

    Workflow:
    1) Reads uploaded file bytes
    2) Stores the file in Azure Blob Storage
    3) Generates a temporary SAS URL for analysis
    4) Selects the processing engine (Document Intelligence / OpenAI / Compare)
    5) Returns the analysis result along with storage metadata

    Args:
        file (UploadFile):
            Uploaded receipt image provided by the API layer.
        method (str):
            Processing engine identifier. Supported values: "di", "openai", "compare".

    Returns:
        dict:
            Receipt metadata and extracted receipt fields.

    Raises:
        ValueError:
            If an unsupported processing method is provided.
    """
    # read uploaded file
    file_bytes = await file.read()

    # generate new filename
    name, ext = os.path.splitext(file.filename)
    new_name = f"{int(time.time())}_{uuid.uuid4().hex}{ext}"  # switched to using the full UUID to prevent from collisions

    # store in Blob Storage
    blob_url = blob_storage.upload_bytes(new_name, file_bytes)

    # generate SAS URL
    sas_url = blob_storage.generate_read_sas(new_name)

    # select processing engine
    if method == "di":
        raw_result = await di_service.analyze_receipt(sas_url)
        analysis = normalize_di_receipt(raw_result)

        save_receipt(db, analysis)

        return ReceiptAnalysisResponse(
            file_saved_as=new_name,
            blob_url=blob_url,
            method="di",
            analysis=analysis,
        )

    elif method == "openai":
        analysis = await processor.analyze_receipt(sas_url)

        save_receipt(db, analysis)

        return ReceiptAnalysisResponse(
            file_saved_as=new_name,
            blob_url=blob_url,
            method="openai",
            analysis=analysis,
        )

    elif method == "compare":
        # run both analyses in parallel
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
