from PyQt6.QtCore import QObject, pyqtSignal
from model.file_loader import ModelError
from model.json_parser import ParserError

class LoadOpenPointDataWorker(QObject):
    """Worker class to run loading task in background thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    json_loaded = pyqtSignal(str)

    def __init__(self, file_path, file_loader, json_parser):
        super().__init__()
        self.file_path = file_path
        self.file_loader = file_loader
        self.json_parser = json_parser

    def run(self):
        try:
            print(f"Loading and parsing JSON from: {self.file_path}")
            content = self.file_loader.load_text_file(self.file_path)
            # Parse the content to ensure it's valid JSON and get pretty string
            _, pretty_json = self.json_parser.parse_pose_json(content)
            self.json_loaded.emit(pretty_json)
            self.finished.emit()
        except (ModelError, ParserError) as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error in ViewModel: {str(e)}")
