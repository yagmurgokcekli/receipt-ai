from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from src.schemas.receipt import ReceiptSchema
from src.schemas.receipt import ReceiptItem


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
