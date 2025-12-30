from app.settings import settings
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas


connection_str = settings.AZURE_BLOB_CONNECTION_STRING
container_name = settings.AZURE_BLOB_CONTAINER

if not connection_str:
    raise ValueError("AZURE_BLOB_CONNECTION_STRING is missing in .env")
if not container_name:
    raise ValueError("AZURE_BLOB_CONTAINER is missing in .env")

blob_service = BlobServiceClient.from_connection_string(connection_str)
container_client = blob_service.get_container_client(container_name)

# container yoksa oluştur
try:
    container_client.create_container()
except Exception:
    pass


def upload_file_to_blob(filename: str, data: bytes):
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url


def generate_sas_url(blob_name: str) -> str:
    blob_client = container_client.get_blob_client(blob_name)

    account_name = blob_service.account_name
    account_key = blob_service.credential.account_key

    sas_token = generate_blob_sas(
        account_name=str(account_name),
        container_name=container_name,
        blob_name=blob_name,
        account_key=str(account_key),
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=2),
    )

    return f"{blob_client.url}?{sas_token}"
