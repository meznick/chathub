import tempfile
import os
from io import BytesIO
from typing import Optional


class TempFileManager:
    """
    Class for managing temporary file names.

    # Example usage
    # manager = TempFileManager()
    # temp_path = manager.create_temp_file()
    # manager.delete_temp_file(temp_path)
    """
    files = set()

    def __init__(self, root: Optional[str] = '/tmp/'):
        self.root = root

    def create_temp_file(self, suffix: Optional[str]) -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.root)
        os.close(fd)
        self.files.add(path)
        return path

    def write_into_file(self, path: str, content: BytesIO):
        if path in self.files:
            with open(path, 'wb') as f:
                f.write(content.read())
        else:
            raise FileNotFoundError(f"File {path} does not exist or already deleted.")

    def delete_temp_file(self, path: str):
        if path in self.files:
            os.remove(path)
            self.files.remove(path)
        else:
            raise FileNotFoundError(f"File {path} does not exist or already deleted.")

    def clear(self):
        for path in self.files:
            os.remove(path)
        self.files.clear()
