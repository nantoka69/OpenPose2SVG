from PyQt6.QtCore import QObject, pyqtSignal
import time
from model.file_loader import ModelError
from model.json_parser import ParserError

class LoadOpenPointDataWorker(QObject):
    """Worker class to run loading task in background thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    json_loaded = pyqtSignal(str)
    rendering_started = pyqtSignal()

    def __init__(self, file_path, file_loader, json_parser):
        super().__init__()
        self.file_path = file_path
        self.file_loader = file_loader
        self.json_parser = json_parser

    def run(self):
        try:
            print(f"[Worker] Starting file load for: {self.file_path}")
            content = self.file_loader.load_text_file(self.file_path)

            print("[Worker] Starting JSON parsing...")
            _, pretty_json = self.json_parser.parse_pose_json(content)

            print("[Worker] Parsing complete, emitting json_loaded signal")
            self.json_loaded.emit(pretty_json)

            print("[Worker] File loaded successfully. Emitting rendering_started signal...")
            self.rendering_started.emit()

            print("[Worker] Rendering complete. Emitting finished signal...")
            self.finished.emit()
        except (ModelError, ParserError) as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error in ViewModel: {str(e)}")
