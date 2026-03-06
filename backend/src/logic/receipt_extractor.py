from typing import cast
from src.schemas.receipt import ReceiptSchema
from src.services.openai_service import OpenAIVisionService
from src.utils.currency_resolver import resolve_currency_from_text


class ReceiptOpenAIProcessor:

    def __init__(self, service: OpenAIVisionService):
        self._svc = service

    async def analyze_receipt(self, image_url: str) -> ReceiptSchema:

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
            user_prompt="Extract receipt data using the provided schema.",
        )

        if result.model is None:
            return ReceiptSchema(source="openai")

        model: ReceiptSchema = cast(ReceiptSchema, result.model)

        model.source = "openai"

        if not model.currency:
            visible_text = await self._svc.extract_visible_text(image_url=image_url)
            resolved = resolve_currency_from_text(visible_text)

            if resolved:
                model.currency = resolved

        return model
