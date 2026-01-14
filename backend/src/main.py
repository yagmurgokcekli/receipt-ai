from fastapi import FastAPI
from src.api.receipts_api import router as receipts_router

app = FastAPI(
    title="Receipt AI Backend",
    description=(
        "Backend service that processes receipt images using multiple AI engines "
        "(Azure Document Intelligence & Azure OpenAI). "
        "Exposes HTTP APIs only — business logic lives in the logic layer."
    ),
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "receipt-ai"}


# Register receipt API routes.
# Routers group domain-level features under a structured URL namespace.
app.include_router(receipts_router, prefix="/api/receipts", tags=["receipts"])
