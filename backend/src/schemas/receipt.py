from __future__ import annotations
from datetime import date, datetime
from typing import Optional, List, Literal
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


class ReceiptAnalysisResponse(BaseModel):
    file_saved_as: str
    blob_url: str
    method: Literal["di", "openai"]
    analysis: ReceiptSchema


class FieldDiff(BaseModel):
    field: str = Field(
        ..., description="Top-level field name being compared (e.g. total, currency)."
    )
    di: Optional[object] = Field(
        default=None, description="Value returned by Document Intelligence."
    )
    openai: Optional[object] = Field(
        default=None, description="Value returned by OpenAI."
    )
    match: bool = Field(
        ..., description="Whether the values are considered equal for this field."
    )


class ItemDiff(BaseModel):

    key: Optional[str] = None  # debug için
    di_item: Optional[ReceiptItem] = None
    openai_item: Optional[ReceiptItem] = None
    status: Literal["matched", "changed", "missing_in_di", "missing_in_openai"] = (
        "matched"
    )
    changed_fields: List[str] = Field(default_factory=list)


class ReceiptDiffReport(BaseModel):
    """
    Diff report between DI and OpenAI outputs.
    """

    matched_count: int = 0
    changed_count: int = 0
    missing_in_di_count: int = 0
    missing_in_openai_count: int = 0

    fields: List[FieldDiff] = Field(default_factory=list)
    items: List[ItemDiff] = Field(default_factory=list)
    summary: str = Field(
        default="pending", description="Human-readable summary of comparison."
    )


class ReceiptCompareAnalysis(BaseModel):
    di: ReceiptSchema
    openai: ReceiptSchema
    diff: ReceiptDiffReport


class ReceiptCompareResponse(BaseModel):
    file_saved_as: str
    blob_url: str
    method: Literal["compare"]
    analysis: ReceiptCompareAnalysis


class ReceiptListSchema(BaseModel):
    id: int
    merchant: Optional[str]
    total: Optional[float]
    currency: Optional[str]
    transaction_date: Optional[date]
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}
