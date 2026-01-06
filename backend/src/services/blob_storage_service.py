from src.settings import settings
from datetime import datetime, timedelta, timezone
from typing import Optional, cast
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    BlobSasPermissions,
    generate_blob_sas
)
import logging
from azure.core.exceptions import ResourceExistsError

logger = logging.getLogger(__name__)


class BlobStorageService:
    """
    Infrastructure-level reusable Azure Blob Storage client.

    This service abstracts storage operations so that application logic
    never depends on Azure SDK primitives directly. It can be reused
    across multiple projects or swapped behind an interface if needed.

    Responsibilities:
        • Manage container lifecycle
        • Upload & delete blobs
        • Generate secure temporary SAS URLs for read access

    This class intentionally does not implement business rules — it only
    exposes storage capabilities in a clean, minimal API surface.
    """

    def __init__(
        self,
        connection_string: str,
        container_name: str,
        auto_create_container: bool = True,
    ):
        """
        Create a storage service bound to a specific container.

        Args:
            connection_string (str):
                Azure Storage connection string.
            container_name (str):
                Target blob container name.
            auto_create_container (bool, optional):
                Automatically create container if missing. Defaults to True.

        Raises:
            ValueError:
                If required configuration values are missing.
        """
        if not connection_string:
            raise ValueError("Missing Azure Blob connection string")

        if not container_name:
            raise ValueError("Missing Azure Blob container name")

        # initialize client & container
        self._client = BlobServiceClient.from_connection_string(connection_string)
        self._container_name = container_name
        self._container = self._client.get_container_client(container_name)

        # create container if needed
        if auto_create_container:
            self._ensure_container_exists()

    # ----- internal helpers -----

    def _ensure_container_exists(self) -> None:
        """Create container if it does not already exist."""
        try:
            self._container.create_container()
            logger.info("Blob container created: %s", self._container_name)

        except ResourceExistsError:
            # normal case — container already exists
            logger.info("Blob container already exists: %s", self._container_name)

        except Exception as e:
            # real failure — must not be ignored
            logger.error(
                "Failed to create blob container %s: %s",
                self._container_name,
                e
            )   
            raise

    def get_blob_client(self, blob_name: str) -> BlobClient:
        """Return a blob-scoped client for the given name."""
        return self._container.get_blob_client(blob_name)

    # ----- public reusable operations -----

    def upload_bytes(self, blob_name: str, data: bytes, overwrite: bool = True) -> str:
        """
        Upload raw bytes and return the full blob URL.

        Args:
            blob_name (str):
                Destination blob name.
            data (bytes):
                File content to upload.
            overwrite (bool, optional):
                Replace existing blob. Defaults to True.

        Returns:
            str: Public blob URL (not SAS-protected).
        """
        blob = self.get_blob_client(blob_name)
        blob.upload_blob(data, overwrite=overwrite)
        return blob.url

    def delete_blob(self, blob_name: str) -> None:
        """
        Delete a blob if it exists.

        Args:
            blob_name (str): Target blob to remove.
        """
        blob = self.get_blob_client(blob_name)
        blob.delete_blob(ignore_if_missing=True)

    def generate_read_sas(
        self,
        blob_name: str,
        expires_in_hours: int = 2,
    ) -> str:
        """
        Generate a temporary read-only SAS URL for a blob.

        Args:
            blob_name (str):
                Blob name to expose.
            expires_in_hours (int, optional):
                Token lifetime. Defaults to 2 hours.

        Returns:
            str: Signed SAS URL granting time-limited read access.

        Raises:
            RuntimeError:
                When account key cannot be resolved from the client.
        """
        blob = self.get_blob_client(blob_name)

        # extract account credentials from storage client
        account_name = cast(str, self._client.account_name)
        account_key = cast(str, getattr(self._client.credential, "account_key", None))

        if not account_key:
            raise RuntimeError(
                "BlobServiceClient has no account_key (Managed Identity?)"
            )

        # generate SAS token
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self._container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        )

        return f"{blob.url}?{sas_token}"


class LazyBlobStorageService:
    """
    Lazy-initializing proxy for :class:`BlobStorageService`.

    This defers creation of the underlying BlobStorageService instance
    (and use of environment-dependent settings) until the first time
    the service is actually used. This improves testability and avoids
    import-time failures in environments where blob storage is not needed.
    """

    def __init__(self) -> None:
        self._impl: Optional[BlobStorageService] = None

    def _get_impl(self) -> BlobStorageService:
        """
        Create the underlying BlobStorageService instance on first use.
        """
        if self._impl is None:
            self._impl = BlobStorageService(
                connection_string=settings.AZURE_BLOB_CONNECTION_STRING,
                container_name=settings.AZURE_BLOB_CONTAINER,
            )
        return self._impl

    def __getattr__(self, name: str):
        """
        Delegate attribute access to the underlying BlobStorageService.
        """
        return getattr(self._get_impl(), name)


# reusable singleton instance (lazily initialized)
blob_storage = LazyBlobStorageService()
