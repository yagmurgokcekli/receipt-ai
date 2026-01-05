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
                "You are a receipt extraction assistant. "
                "Return only factual values. If a field is missing, return null."
            ),
            user_prompt=(
                "Extract merchant, total, transaction_date and items from this receipt."
            ),
        )

        if result.model is not None:
            return result.model.model_dump()
        return {}
