from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    AZURE_BLOB_CONNECTION_STRING: str
    AZURE_BLOB_CONTAINER: str

    AZURE_DI_ENDPOINT: str
    AZURE_DI_KEY: str

    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str

    DATABASE_URL: str

    model_config = {"env_file": str(ENV_PATH)}


settings = Settings()  # type: ignore
