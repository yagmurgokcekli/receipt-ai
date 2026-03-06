from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.receipts_api import router as receipts_router
from src.api.dashboard_api import router as dashboard_router


app = FastAPI(
    title="Receipt AI Backend",
    description=(
        "Backend service that processes receipt images using multiple AI engines "
        "(Azure Document Intelligence & Azure OpenAI). "
        "Exposes HTTP APIs only — business logic lives in the logic layer."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "receipt-ai"}


# Register receipt API routes.
# Routers group domain-level features under a structured URL namespace.
app.include_router(receipts_router, prefix="/api/receipts", tags=["receipts"])
app.include_router(dashboard_router, prefix="/api")
