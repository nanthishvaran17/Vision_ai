from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    async def save_file(self, content: bytes, filename: str, subfolder: str = "images") -> str:
        """Saves content and returns relative storage path or URI."""
        pass

    @abstractmethod
    async def get_file(self, path: str) -> bytes:
        """Retrieves content by path/URI."""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Deletes file by path/URI."""
        pass
