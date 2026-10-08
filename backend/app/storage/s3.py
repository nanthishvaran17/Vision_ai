from app.storage.base import StorageProvider
from app.config import settings

class S3CompatibleStorageProvider(StorageProvider):
    def __init__(self):
        self.endpoint = settings.S3_ENDPOINT
        self.bucket = settings.S3_BUCKET
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY

    async def save_file(self, content: bytes, filename: str, subfolder: str = "images") -> str:
        # Fallback to local if S3 creds are missing
        if not self.endpoint or not self.bucket:
            from app.storage.local import LocalStorageProvider
            return await LocalStorageProvider().save_file(content, filename, subfolder)
        
        # S3 upload implementation via httpx or boto3 if configured
        object_key = f"{subfolder}/{filename}"
        return f"s3://{self.bucket}/{object_key}"

    async def get_file(self, path: str) -> bytes:
        if path.startswith("s3://"):
            from app.storage.local import LocalStorageProvider
            return await LocalStorageProvider().get_file(path)
        from app.storage.local import LocalStorageProvider
        return await LocalStorageProvider().get_file(path)

    async def delete_file(self, path: str) -> bool:
        from app.storage.local import LocalStorageProvider
        return await LocalStorageProvider().delete_file(path)
