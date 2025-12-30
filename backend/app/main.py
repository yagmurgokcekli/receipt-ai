import os, time
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.blob_service import upload_file_to_blob, generate_sas_url
from app.services.document_intelligence_service import analyze_receipt_with_di
from app.services.openai_service import analyze_receipt_with_openai

app = FastAPI(title="Receipt AI Backend")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "receipt-ai"}


@app.post("/api/receipts")
async def upload_and_analyze(file: UploadFile = File(...), method: str = "di"):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    file_bytes = await file.read()

    # Blob'a kaydet
    name, ext = os.path.splitext(file.filename)
    new_name = f"{int(time.time())}{ext}"
    blob_url = upload_file_to_blob(new_name, file_bytes)

    # SAS URL üret
    sas_url = generate_sas_url(new_name)

    # Analiz motorunu seç
    if method == "di":
        analysis = await analyze_receipt_with_di(sas_url)

    elif method == "openai":
        analysis = await analyze_receipt_with_openai(sas_url)
    else:
        raise HTTPException(
            status_code=400, detail="Invalid method. Use 'di' or 'openai'."
        )

    return {
        "file_saved_as": new_name,
        "blob_url": blob_url,
        "sas_url": sas_url,
        "method": method,
        "analysis": analysis,
    }
