import os
import aiofiles
from app.storage.base import StorageProvider
from app.config import settings

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or settings.UPLOAD_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, content: bytes, filename: str, subfolder: str = "images") -> str:
        target_dir = os.path.join(self.base_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
            
        rel_path = os.path.relpath(file_path, self.base_dir).replace("\\", "/")
        return rel_path

    async def get_file(self, path: str) -> bytes:
        full_path = os.path.join(self.base_dir, path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, path: str) -> bool:
        full_path = os.path.join(self.base_dir, path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
