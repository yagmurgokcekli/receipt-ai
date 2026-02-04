import os
import time
import uuid
import asyncio
import re
from typing import Union, Optional, Tuple, Dict, List
from venv import logger
from sqlalchemy.orm import Session
from collections import defaultdict

from src.db.crud.receipt_crud import save_receipt

from src.schemas.engine import Engine
from src.settings import settings

from src.services.blob_storage_service import blob_storage
from src.services.document_intelligence_service import DocumentIntelligenceService
from src.services.openai_service import OpenAIVisionService

from src.logic.receipt_normalizer import normalize_di_receipt

from src.utils.currency_resolver import resolve_currency_from_text

from src.schemas.receipt import (
    ReceiptItem,
    ReceiptSchema,
    ReceiptAnalysisResponse,
    ReceiptCompareResponse,
    ReceiptCompareAnalysis,
    ItemDiff,
    ReceiptDiffReport,
    FieldDiff,
)


di_service = DocumentIntelligenceService(
    endpoint=settings.AZURE_DI_ENDPOINT,
    api_key=settings.AZURE_DI_KEY,
)

oai_service = OpenAIVisionService(
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    deployment=settings.AZURE_OPENAI_DEPLOYMENT,
)


async def process_receipt(
    file,
    method: str,
    db: Session,
    user_id: int,
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
    if method == Engine.di:
        raw_result = await di_service.analyze_receipt(sas_url)
        analysis = normalize_di_receipt(raw_result)

        try:
            save_receipt(db, analysis, user_id)
        except Exception as e:
            logger.exception("Failed to persist receipt")
            raise

        return ReceiptAnalysisResponse(
            file_saved_as=new_name,
            blob_url=blob_url,
            method="di",
            analysis=analysis,
        )

    elif method == Engine.openai:
        analysis = await processor.analyze_receipt(sas_url)

        try:
            save_receipt(db, analysis, user_id)
        except Exception as e:
            logger.exception("Failed to persist receipt")
            raise

        return ReceiptAnalysisResponse(
            file_saved_as=new_name,
            blob_url=blob_url,
            method="openai",
            analysis=analysis,
        )

    elif method == Engine.compare:
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


class ReceiptOpenAIProcessor:
    """
    Business-level receipt processor that uses the reusable OpenAI vision service.

    This class does not perform low-level API calls. Instead, it applies
    domain semantics on top of the shared OpenAI service and converts
    model output into a receipt-focused structure.

    Responsibilities:
    - Call the OpenAI vision service with a receipt-specific schema
    - Enforce business meaning (merchant, total, date, items)
    - Return normalized dictionary output for upstream layers
    """

    def __init__(self, service: OpenAIVisionService):
        self._svc = service

    async def analyze_receipt(self, image_url: str) -> ReceiptSchema:
        """
        Analyze a receipt image using OpenAI and extract structured receipt fields.

        Args:
            image_url (str):
                Public or SAS-signed URL of the receipt image.

        Returns:
            ReceiptSchema: Parsed receipt fields (typed Pydantic model).
        """

        result = await self._svc.analyze_image_with_schema(
            image_url=image_url,
            schema_model=ReceiptSchema,
            system_prompt=(
                "You are a strictly factual receipt extraction engine.\n"
                "You must populate ONLY the fields defined in the provided schema.\n"
                "Field meanings, constraints, and formatting rules are defined "
                "exclusively in the schema descriptions.\n\n"
                "Rules:\n"
                "- Use only information explicitly visible in the image.\n"
                "- Do not infer, guess, calculate, translate, or normalize values.\n"
                "- If a field cannot be populated with certainty, return null.\n"
                "- Do not add, remove, or rename fields.\n"
                "- Output must strictly conform to the schema."
            ),
            user_prompt=("Extract receipt data using the provided schema."),
        )

        # If parsing fails or model is missing, return an "empty" schema
        if result.model is None:
            return ReceiptSchema(source="openai")

        # `result.model` is already a ReceiptSchema instance (typed)
        model: ReceiptSchema = result.model  # type: ignore[assignment]

        # Force invariant field (never allow model to change it)
        model.source = "openai"

        # Lazy OCR currency resolution (only if missing)
        if not model.currency:
            visible_text = await self._svc.extract_visible_text(image_url=image_url)
            resolved = resolve_currency_from_text(visible_text)
            if resolved:
                model.currency = resolved

        return model


processor = ReceiptOpenAIProcessor(oai_service)


def normalize_item_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    # collapse whitespace into single spaces
    text = re.sub(r"\s+", " ", name).strip()
    return text.casefold()


def normalize_number(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    # round to 2 decimal places
    return round(float(x), 2)


def item_key(
    item: ReceiptItem,
) -> Tuple[Optional[str], Optional[float], Optional[float]]:
    return (
        normalize_item_name(item.name),
        normalize_number(item.quantity),
        normalize_number(item.price),
    )


def build_diff(di: ReceiptSchema, openai: ReceiptSchema) -> ReceiptDiffReport:
    """
    Build a strict, deterministic diff between Document Intelligence and OpenAI
    receipt extraction results.

    Top-level fields are compared by direct equality.
    Line items are matched using a strict key (normalized name, quantity, price)
    without semantic or fuzzy inference.
    """

    def eq(a, b) -> bool:
        return a == b

    fields = [
        FieldDiff(
            field="merchant",
            di=di.merchant,
            openai=openai.merchant,
            match=eq(di.merchant, openai.merchant),
        ),
        FieldDiff(
            field="total",
            di=di.total,
            openai=openai.total,
            match=eq(di.total, openai.total),
        ),
        FieldDiff(
            field="currency",
            di=di.currency,
            openai=openai.currency,
            match=eq(di.currency, openai.currency),
        ),
        FieldDiff(
            field="transaction_date",
            di=di.transaction_date,
            openai=openai.transaction_date,
            match=eq(di.transaction_date, openai.transaction_date),
        ),
    ]

    di_items = di.items or []
    oai_items = openai.items or []

    # index items by key
    di_index: Dict[tuple, List[ReceiptItem]] = defaultdict(list)
    for it in di_items:
        di_index[item_key(it)].append(it)

    oai_index: Dict[tuple, List[ReceiptItem]] = defaultdict(list)
    for it in oai_items:
        oai_index[item_key(it)].append(it)

    all_keys = set(di_index.keys()) | set(oai_index.keys())

    item_diffs: List[ItemDiff] = []
    matched = changed = missing_di = missing_openai = 0

    for k in sorted(all_keys, key=lambda x: (x[0] or "", x[1] or 0, x[2] or 0)):
        di_list = di_index.get(k, [])
        oai_list = oai_index.get(k, [])

        # consume pairs for duplicates
        while di_list or oai_list:
            di_item = di_list.pop() if di_list else None
            oai_item = oai_list.pop() if oai_list else None

            if di_item and oai_item:
                # both present -> matched
                matched += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=di_item,
                        openai_item=oai_item,
                        status="matched",
                    )
                )
            elif di_item and not oai_item:
                missing_openai += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=di_item,
                        openai_item=None,
                        status="missing_in_openai",
                    )
                )
            elif oai_item and not di_item:
                missing_di += 1
                item_diffs.append(
                    ItemDiff(
                        key=str(k),
                        di_item=None,
                        openai_item=oai_item,
                        status="missing_in_di",
                    )
                )

    # summary string
    mismatches = [f.field for f in fields if not f.match]
    summary_parts = []
    if mismatches:
        summary_parts.append(f"Field mismatches: {', '.join(mismatches)}")
    else:
        summary_parts.append("Top-level fields match.")

    summary_parts.append(
        f"Items: matched={matched}, missing_in_di={missing_di}, missing_in_openai={missing_openai}"
    )

    return ReceiptDiffReport(
        fields=fields,
        items=item_diffs,
        matched_count=matched,
        changed_count=changed,
        missing_in_di_count=missing_di,
        missing_in_openai_count=missing_openai,
        summary=" | ".join(summary_parts),
    )
