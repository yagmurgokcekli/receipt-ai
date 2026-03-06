from typing import List, Dict
import json
from datetime import datetime

from src.services.openai_service import OpenAIVisionService


CATEGORIES = [
    "Food",
    "Fuel",
    "Electronics",
    "Clothing",
    "Health",
    "Transport",
    "Entertainment",
    "Other",
]


class ExpenseClassifier:
    def __init__(self, openai_service: OpenAIVisionService):
        self._svc = openai_service

    async def classify_items(
        self,
        items: List[str],
        merchant: str | None = None,
    ) -> Dict[str, str]:

        if not items:
            return {}

        items_list = "\n".join([f"- {item}" for item in items if item])

        prompt = f"""
You are a financial expense classifier.

Classify each receipt item into ONE of the following categories:

{", ".join(CATEGORIES)}

Merchant: {merchant}

Items:
{items_list}

Return STRICT JSON in this format:

[
  {{"item": "Milk", "category": "Food"}},
  {{"item": "Diesel", "category": "Fuel"}}
]

Return ONLY JSON.
"""

        response = await self._svc._client.chat.completions.create(
            model=self._svc._deployment,
            temperature=0,
            messages=[
                {"role": "system", "content": "You classify expense items."},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content
        if not content:
            return {}

        parsed = json.loads(content)

        return {entry["item"]: entry["category"] for entry in parsed}
