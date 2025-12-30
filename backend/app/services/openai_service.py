from app.settings import settings
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from typing import List, Optional
import json


endpoint = settings.AZURE_OPENAI_ENDPOINT
api_key = settings.AZURE_OPENAI_KEY
deployment = settings.AZURE_OPENAI_DEPLOYMENT

if not endpoint:
    raise RuntimeError("AZURE_OPENAI_ENDPOINT is missing in .env")
if not api_key:
    raise RuntimeError("AZURE_OPENAI_KEY is missing in .env")
if not deployment:
    raise RuntimeError("AZURE_OPENAI_DEPLOYMENT is missing in .env")


client_oa = AsyncAzureOpenAI(
    azure_endpoint=endpoint, api_key=api_key, api_version="2024-08-01-preview"
)


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


async def analyze_receipt_with_openai(image_url: str) -> dict:
    try:
        response = await client_oa.chat.completions.create(
            model=deployment,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a receipt extraction assistant. "
                        "Return JSON only. "
                        "If a field is missing, return null."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract the receipt fields: "
                                "merchant, total, transaction_date, items."
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ReceiptSchema",
                    "schema": ReceiptSchema.model_json_schema(),
                },
            },
        )

        raw = response.choices[0].message.content
        if not raw:
            raise ValueError("Empty response from OpenAI")
        data = json.loads(raw)

        return ReceiptSchema(**data).model_dump()

    except Exception as e:
        return {
            "merchant": None,
            "total": None,
            "transaction_date": None,
            "items": None,
            "source": "openai",
            "error": str(e),
        }
