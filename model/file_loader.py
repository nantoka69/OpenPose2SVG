import os
import time

class ModelError(Exception):
    """Generic exception for the model layer."""
    pass

class FileLoader:
    MAX_FILE_SIZE = 100 * 1024  # 100 KB

    def load_text_file(self, file_path):
        try:
            # Check file size before opening
            if os.path.getsize(file_path) > self.MAX_FILE_SIZE:
                raise ModelError(f"File is too large ({os.path.getsize(file_path)} bytes). Maximum size is {self.MAX_FILE_SIZE} bytes.")

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            if isinstance(e, ModelError):
                raise e
            raise ModelError(str(e))
