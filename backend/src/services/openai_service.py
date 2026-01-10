from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel
from openai import AsyncAzureOpenAI
import json


class OpenAIJsonSchemaResponse(BaseModel):
    """
    Generic wrapper for structured model responses.

    Contains both:
        • `raw`  → decoded JSON returned by the model
        • `model` → parsed Pydantic object (when schema is valid)

    This allows callers to choose between:
        - working with typed objects, or
        - inspecting the raw response payload.
    """

    raw: Dict[str, Any]
    model: Optional[BaseModel] = None


class OpenAIVisionService:
    """
    Reusable Azure OpenAI Vision + Structured Output service.

    This class abstracts away the SDK details and provides a clean,
    project-agnostic API for calling Vision with JSON-Schema responses.

    Responsibilities:
        • Execute Vision requests
        • Enforce structured output contracts
        • Return a parsed Pydantic model + raw payload

    It intentionally contains **no business / receipt logic** so it can be
    reused across different domains and projects.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str = "2024-08-01-preview",
    ):
        """
        Initialize Azure OpenAI client.

        Args:
            endpoint (str): Azure OpenAI endpoint URL.
            api_key (str): API key for authentication.
            deployment (str): Model deployment name.
            api_version (str): API version to use (defaults to Vision preview).

        Raises:
            ValueError: If any required configuration is missing.
        """
        if not endpoint:
            raise ValueError("Missing OpenAI endpoint")
        if not api_key:
            raise ValueError("Missing OpenAI api_key")
        if not deployment:
            raise ValueError("Missing OpenAI deployment name")

        self._deployment = deployment
        self._client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    async def analyze_image_with_schema(
        self,
        image_url: str,
        schema_model: type[BaseModel],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0,
    ) -> OpenAIJsonSchemaResponse:
        """
        Execute a Vision request and enforce JSON-Schema structured output.

        This method is intentionally generic — the caller decides:
            • which schema to use
            • what the task prompt is
            • how the result will be interpreted

        Args:
            image_url (str): Public or SAS-secured image URL.
            schema_model (BaseModel): Pydantic model defining output schema.
            system_prompt (str): Instruction prompt for model behavior.
            user_prompt (str): Task-specific request text.
            temperature (float): Sampling temperature (default = 0).

        Returns:
            OpenAIJsonSchemaResponse:
                • raw decoded JSON dictionary
                • parsed Pydantic model instance

        Raises:
            ValueError: If the model returns an empty or invalid response.
        """

        response = await self._client.chat.completions.create(
            model=self._deployment,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_model.__name__,
                    "schema": schema_model.model_json_schema(),
                },
            },
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")

        # parse JSON -> then validate into typed model
        raw_data = json.loads(content)
        model_obj = schema_model(**raw_data)

        return OpenAIJsonSchemaResponse(
            raw=raw_data,
            model=model_obj,
        )

    async def extract_visible_text(
        self,
        image_url: str,
        temperature: float = 0,
    ) -> str:
        """
        Extract ALL visible text from an image as-is (OCR-like).
        Returns plain text (not JSON).
        """

        response = await self._client.chat.completions.create(
            model=self._deployment,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an OCR engine. Extract all visible text from the image "
                        "exactly as it appears. Preserve symbols ($, €, ₺), punctuation, "
                        "and line breaks as much as possible. Do not summarize or interpret."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all visible text from this receipt.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
        )

        return response.choices[0].message.content or ""
