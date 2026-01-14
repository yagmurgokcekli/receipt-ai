from src.services.openai_service import OpenAIVisionService
from src.schemas.receipt import ReceiptSchema
from src.utils.currency_resolver import resolve_currency_from_text


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
