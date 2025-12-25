import time
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.blob_service import upload_file_to_blob, generate_sas_url
from app.services.document_intelligence_service import analyze_receipt_with_di



app = FastAPI(title="Receipt AI Backend")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "receipt-ai"}

@app.post("/api/receipts/upload")
async def upload_receipt(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    file_bytes = await file.read()

    name, ext = os.path.splitext(file.filename)
    new_filename = f"{int(time.time())}{ext}"

    blob_url = upload_file_to_blob(new_filename, file_bytes)

    return {
        "original_name": file.filename,
        "saved_as": new_filename,
        "blob_url": blob_url
    }

@app.post("/api/receipts/upload-and-analyze")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    file_bytes = await file.read()

    # Blob'a kaydet
    name, ext = os.path.splitext(file.filename)
    new_name = f"{int(time.time())}{ext}"
    blob_url = upload_file_to_blob(new_name, file_bytes)

    # SAS URL üret
    sas_url = generate_sas_url(new_name)

    # DI ile analiz et
    analysis = await analyze_receipt_with_di(sas_url)

    return {
        "file_saved_as": new_name,
        "blob_url": blob_url,
        "sas_url": sas_url,
        "analysis": analysis
    }