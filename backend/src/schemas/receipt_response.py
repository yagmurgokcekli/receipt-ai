from pydantic import BaseModel
from typing import Literal

from src.schemas.receipt import ReceiptSchema


class ReceiptAnalysisResponse(BaseModel):
    file_saved_as: str
    blob_url: str
    method: Literal["di", "openai"]
    analysis: ReceiptSchema
