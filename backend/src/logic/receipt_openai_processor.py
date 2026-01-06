from typing import Optional, List
from pydantic import BaseModel

from src.services.openai_service import OpenAIVisionService


class ReceiptItem(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None


class ReceiptSchema(BaseModel):
    merchant: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    transaction_date: Optional[str] = None
    items: Optional[List[ReceiptItem]] = None
    source: str = "openai"


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

    async def analyze_receipt(self, image_url: str) -> dict:
        """
        Analyze a receipt image using OpenAI and extract structured receipt fields.

        Args:
            image_url (str):
                Public or SAS-signed URL of the receipt image.

        Returns:
            dict:
                Parsed receipt fields such as merchant, total, date, and items.
                Returns an empty dict if parsing fails or no data is extracted.
        """
        result = await self._svc.analyze_image_with_schema(
            image_url=image_url,
            schema_model=ReceiptSchema,
            system_prompt=(
                "You are a strictly factual receipt extraction engine. "
                "Return only values that are explicitly visible in the image. "
                "If a field is missing, return null. Do NOT infer or guess."
            ),
            user_prompt=(
                "Extract receipt data using the following exact field rules.\n\n"
                "Output fields MUST match Document Intelligence semantics:\n"
                "- merchant : store name exactly as printed\n"
                "- total : numeric value of grand total (no currency symbol)\n"
                "- currency : currency code derived ONLY from explicit symbols or text "
                "(for example $, USD, ₺, TRY, €, EUR). If uncertain, return null.\n"
                "- transaction_date : purchase date in ISO-like format YYYY-MM-DD "
                "(do NOT include time unless it is explicitly present).\n\n"
                "Items must be an array where each item contains:\n"
                "- name : line item description\n"
                "- quantity : numeric quantity if visible, else null\n"
                "- price : line item total price if visible, else null\n\n"
                "Important extraction rules:\n"
                "- Do not fabricate any values; return null for missing fields.\n"
                "- Do not infer tax or totals — extract only printed values.\n"
                "- Return strictly structured JSON matching the schema. "
                "Do not add extra fields.\n"
            ),
        )

        if result.model is not None:
            return result.model.model_dump()
        return {}
