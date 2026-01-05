from typing import Any, Dict, List
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceService:
    """
    Infrastructure-level wrapper around Azure Document Intelligence.

    This service isolates all SDK interactions and exposes a small,
    reusable API that can be consumed by business logic without
    binding the domain layer to Azure library types.

    Responsibilities:
        • Execute model analysis requests
        • Return raw SDK results when needed
        • Provide higher-level helpers for common receipt scenarios

    This class deliberately performs **no domain validation or normalization**.
    It focuses only on retrieving structured data from Azure DI.
    """

    def __init__(self, endpoint: str, api_key: str):
        """
        Create a DI client bound to a specific endpoint and key.

        Args:
            endpoint (str): Azure Document Intelligence endpoint URL.
            api_key (str): Access key for the DI resource.

        Raises:
            ValueError: If configuration values are missing.
        """
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    async def run_analysis(self, model_id: str, url: str) -> AnalyzeResult:
        """
        Execute a DI model and return the raw AnalyzeResult.

        This method intentionally returns the SDK type so that callers
        who need full control may inspect pages, spans, confidence values, etc.

        Args:
            model_id (str): ID of the model to run (e.g., 'prebuilt-receipt').
            url (str): Public or SAS-secured document URL.

        Returns:
            AnalyzeResult: Raw SDK result object from Azure DI.
        """
        req = AnalyzeDocumentRequest(url_source=url)

        poller = await self._client.begin_analyze_document(
            model_id=model_id,
            body=req,
        )

        return await poller.result()

    async def analyze_receipt(self, url: str) -> Dict[str, Any]:
        """
        Convenience wrapper for `prebuilt-receipt`.

        Converts the DI response into a lightweight dictionary format
        that is easier for higher layers to consume. This method extracts
        only the fields commonly expected in a receipt use-case.

        Args:
            url (str): Document URL to analyze.

        Returns:
            dict: Receipt-like structure containing merchant, total,
                  transaction_date and parsed item lines.
        """
        result = await self.run_analysis("prebuilt-receipt", url)

        docs = result.documents or []
        doc = docs[0] if docs else None
        fields: Dict[str, Any] = getattr(doc, "fields", {}) or {}

        def safe(name: str):
            """Return best-available value from a DI field."""
            f = fields.get(name)
            if not f:
                return None
            return (
                getattr(f, "value_object", None)
                or getattr(f, "value_string", None)
                or getattr(f, "value_number", None)
                or getattr(f, "content", None)
            )

        # extract line items
        items: List[Dict[str, Any]] = []
        items_field = fields.get("Items")
        value_array = getattr(items_field, "value_array", None)

        if value_array:
            for row in value_array:
                obj = getattr(row, "value_object", None)
                if not obj:
                    continue

                def cell(k):
                    f = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
                    return getattr(f, "value_string", None) or getattr(
                        f, "content", None
                    )

                items.append(
                    {
                        "description": cell("Description"),
                        "quantity": cell("Quantity"),
                        "price": cell("Price"),
                        "total_price": cell("TotalPrice"),
                    }
                )

        return {
            "merchant": safe("MerchantName") or safe("MerchantAddress"),
            "total": safe("Total") or safe("Subtotal"),
            "transaction_date": safe("TransactionDate"),
            "items": items or None,
            "source": "document_intelligence",
        }
