from PyQt6.QtCore import QObject, pyqtSignal
from model.file_handler import ModelError

class SaveSvgWorker(QObject):
    """Worker class to run saving task in background thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_path, svg_content, file_handler):
        super().__init__()
        self.file_path = file_path
        self.svg_content = svg_content
        self.file_handler = file_handler

    def run(self):
        try:
            print(f"[Worker] Saving SVG to: {self.file_path}")
            self.file_handler.save_text_file(self.file_path, self.svg_content)
            print("[Worker] SVG saved successfully. Emitting finished signal...")
            self.finished.emit()
        except ModelError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error during save: {str(e)}")
