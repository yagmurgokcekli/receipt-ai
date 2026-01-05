import os, time
from src.settings import settings

from src.services.blob_storage_service import blob_storage
from src.services.document_intelligence_service import DocumentIntelligenceService
from src.services.openai_service import OpenAIVisionService

from src.logic.receipt_openai_processor import ReceiptOpenAIProcessor


di_service = DocumentIntelligenceService(
    endpoint=settings.AZURE_DI_ENDPOINT,
    api_key=settings.AZURE_DI_KEY,
)

oai_service = OpenAIVisionService(
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    deployment=settings.AZURE_OPENAI_DEPLOYMENT,
)

processor = ReceiptOpenAIProcessor(oai_service)


async def process_receipt(file, method: str):
    """
    Orchestrates the full receipt-processing workflow.

    This function acts as the application-level coordinator. It does not
    perform low-level logic itself, but delegates responsibilities to
    reusable infrastructure and domain services.

    Workflow:
    1) Reads uploaded file bytes
    2) Stores the file in Azure Blob Storage
    3) Generates a temporary SAS URL for analysis
    4) Selects the processing engine (Document Intelligence / OpenAI)
    5) Returns the analysis result along with storage metadata

    Args:
        file (UploadFile):
            Uploaded receipt image provided by the API layer.
        method (str):
            Processing engine identifier. Supported values: "di", "openai".

    Returns:
        dict:
            Receipt metadata and extracted receipt fields.

    Raises:
        ValueError:
            If an unsupported processing method is provided.
    """
    # read uploaded file
    file_bytes = await file.read()

    # generate new filename
    name, ext = os.path.splitext(file.filename)
    new_name = f"{int(time.time())}{ext}"

    # store in Blob Storage
    blob_url = blob_storage.upload_bytes(new_name, file_bytes)
    
    # generate SAS URL
    sas_url = blob_storage.generate_read_sas(new_name)

    # select processing engine
    if method == "di":
        analysis = await di_service.analyze_receipt(sas_url)

    elif method == "openai":
        analysis = await processor.analyze_receipt(sas_url)

    else:
        raise ValueError("Invalid method")

    return {
        "file_saved_as": new_name,
        "blob_url": blob_url,
        "sas_url": sas_url,
        "method": method,
        "analysis": analysis,
    }
