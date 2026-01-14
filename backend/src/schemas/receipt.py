from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description=(
            "Exact line item name or description as printed on the receipt. "
            "Do not normalize, translate, or infer."
        ),
    )
    quantity: Optional[float] = Field(
        default=None,
        description=(
            "Numeric quantity of the item if explicitly shown on the receipt. "
            "Return null if quantity is not printed."
        ),
    )
    price: Optional[float] = Field(
        default=None,
        description=(
            "Total price for this line item (not unit price unless explicitly stated). "
            "Return null if not visible."
        ),
    )

    model_config = {"from_attributes": True}  # Enable ORM mode


class ReceiptSchema(BaseModel):
    merchant: Optional[str] = Field(
        default=None,
        description=(
            "Merchant or store name exactly as printed on the receipt. "
            "Do not infer brand names or locations."
        ),
    )
    total: Optional[float] = Field(
        default=None,
        description=(
            "Grand total amount paid for the receipt. "
            "Numeric value only, without currency symbols."
        ),
    )
    currency: Optional[str] = Field(
        default=None,
        description=(
            "ISO-like currency code (e.g. TRY, USD, EUR) derived ONLY from explicit "
            "symbols or text visible on the receipt. "
            "Return null if currency is not clearly stated."
        ),
    )
    transaction_date: Optional[date] = Field(
        default=None,
        description=(
            "Purchase date as printed on the receipt, formatted as YYYY-MM-DD. "
            "Do not include time unless explicitly present."
        ),
    )
    items: Optional[List[ReceiptItem]] = Field(
        default=None,
        description=(
            "List of purchased items extracted from the receipt. "
            "Return null if no individual items are listed."
        ),
    )
    source: str = Field(
        default="openai",
        description=(
            "Source system that produced this extraction result. "
            "For OpenAI extractions, this field is always set to 'openai'."
        ),
    )

    model_config = {"from_attributes": True}  # Enable ORM mode
