from app.settings import settings
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential


endpoint = settings.AZURE_DI_ENDPOINT
api_key = settings.AZURE_DI_KEY

if not endpoint:
    raise ValueError("AZURE_DI_ENDPOINT is missing in .env")
if not api_key:
    raise ValueError("AZURE_DI_KEY is missing in .env")

client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(api_key)
)


async def analyze_receipt_with_di(blob_url: str) -> dict:
    req = AnalyzeDocumentRequest(url_source=blob_url)
    poller = await client.begin_analyze_document(model_id="prebuilt-receipt", body=req)
    result = await poller.result()

    docs = result.documents or []
    doc = docs[0] if docs else None
    fields = doc.fields or {} if doc else {}

    def safe(name: str):
        f = fields.get(name)
        if not f:
            return None

        return (
            getattr(f, "value_object", None)
            or getattr(f, "value_string", None)
            or getattr(f, "value_number", None)
            or getattr(f, "content", None)
        )

    items = []
    items_field = fields.get("Items")

    if items_field:
        value_array = getattr(items_field, "value_array", None)
        if value_array:
            for row in value_array:
                obj = getattr(row, "value_object", None)
                if not obj:
                    continue

                def cell(name):
                    f = (
                        obj.get(name)
                        if isinstance(obj, dict)
                        else getattr(obj, name, None)
                    )
                    if not f:
                        return None
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

    merchant = (
        safe("MerchantName") or safe("MerchantAddress") or safe("MerchantPhoneNumber")
    )

    total = safe("Total") or safe("Subtotal") or safe("GrandTotal")
    tx_date = safe("TransactionDate") or safe("TransactionTime")

    return {
        "merchant": merchant,
        "total": total,
        "transaction_date": tx_date,
        "items": items or None,
        "source": "document_intelligence",
    }
