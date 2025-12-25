import os
from dotenv import load_dotenv
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential

load_dotenv()

endpoint = os.getenv("AZURE_DI_ENDPOINT")
api_key = os.getenv("AZURE_DI_KEY")

if not endpoint or not api_key:
    raise ValueError("Document Intelligence credentials are missing in .env")

client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)


async def analyze_receipt_with_di(blob_url: str) -> dict:
    req = AnalyzeDocumentRequest(url_source=blob_url)

    poller = await client.begin_analyze_document(
        model_id="prebuilt-receipt",
        body=req
    )

    result = await poller.result()

    docs = result.documents or []
    doc = docs[0] if docs else None
    fields = doc.fields or {} if doc else {}

    def safe(name: str):
        f = fields.get(name)
        if not f:
            return None

        # value varsa onu al
        val = getattr(f, "value", None)
        if val not in (None, ""):
            return val

        # yoksa content'i fallback olarak al
        return getattr(f, "content", None)

    merchant = safe("MerchantName") or safe("MerchantAddress") or safe("MerchantPhoneNumber")
    total = safe("Total") or safe("Subtotal") or safe("GrandTotal")
    tx_date = safe("TransactionDate") or safe("TransactionTime")

    return {
        "merchant": merchant,
        "total": total,
        "transaction_date": tx_date,
        "raw_available": list(fields.keys()),
        "source": "document_intelligence"
    }