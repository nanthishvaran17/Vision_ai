from app.config import settings
from app.storage.base import StorageProvider
from app.storage.local import LocalStorageProvider
from app.storage.s3 import S3CompatibleStorageProvider

def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_PROVIDER.lower() == "s3":
        return S3CompatibleStorageProvider()
    return LocalStorageProvider()
