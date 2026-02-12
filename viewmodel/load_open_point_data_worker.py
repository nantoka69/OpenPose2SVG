from PyQt6.QtCore import QObject, pyqtSignal
import time
from model.file_handler import ModelError
from model.json_parser import ParserError
from model.svg_renderer import render_pose

class LoadOpenPointDataWorker(QObject):
    """Worker class to run loading task in background thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    json_loaded = pyqtSignal(str)
    on_svg_ready = pyqtSignal(str)
    rendering_started = pyqtSignal()

    def __init__(self, file_path, file_handler, json_parser):
        super().__init__()
        self.file_path = file_path
        self.file_handler = file_handler
        self.json_parser = json_parser

    def run(self):
        try:
            print(f"[Worker] Starting file load for: {self.file_path}")
            content = self.file_handler.load_text_file(self.file_path)

            print("[Worker] Starting JSON parsing...")
            pose_data, pretty_json = self.json_parser.parse_pose_json(content)
            
            print("[Worker] File loaded successfully. Emitting rendering_started signal...")
            self.rendering_started.emit()

            print("[Worker] Starting SVG rendering...")
            svg_content = render_pose(pose_data)
            
            print("[Worker] Processing complete, emitting signals")
            self.json_loaded.emit(pretty_json)
            self.on_svg_ready.emit(svg_content)
            self.finished.emit()
        except ParserError as e:
            self.error.emit(f"Pose file format error: {str(e)}")
        except TypeError as e:
            self.error.emit(f"Pose file format error: {str(e)}")
        except ModelError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error in ViewModel: {str(e)}")
