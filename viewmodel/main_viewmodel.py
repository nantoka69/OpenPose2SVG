from PyQt6.QtCore import QObject, pyqtSignal, QThread
from .load_open_point_data_worker import LoadOpenPointDataWorker

from .error import ViewModelError

class MainViewModel(QObject):
    # Signals for View Layer
    on_json_loaded = pyqtSignal(str)
    on_load_error = pyqtSignal(str)

    def __init__(self, file_loader, json_parser):
        super().__init__()
        self.file_loader = file_loader
        self.json_parser = json_parser
        self.current_json_loader_thread = None
        self.current_json_loader_worker = None
        
    def load_json(self, file_path):
        # Stop existing thread if any
        if self.current_json_loader_thread and self.current_json_loader_thread.isRunning():
            self.current_json_loader_thread.quit()
            self.current_json_loader_thread.wait()

        self.current_json_loader_thread = QThread()
        self.current_json_loader_worker = LoadOpenPointDataWorker(file_path, self.file_loader, self.json_parser)
        
        self.current_json_loader_worker.moveToThread(self.current_json_loader_thread)
        
        # Connect signals
        self.current_json_loader_thread.started.connect(self.current_json_loader_worker.run)
        self.current_json_loader_worker.json_loaded.connect(self.__handle_json_loaded)
        self.current_json_loader_worker.finished.connect(self.__handle_json_loader_worker_finished)
        self.current_json_loader_worker.error.connect(self.__handle_worker_error)
        
        self.current_json_loader_thread.start()

    def __handle_json_loaded(self, pretty_json):
        self.on_json_loaded.emit(pretty_json)

    def __handle_json_loader_worker_finished(self):
        if self.current_json_loader_thread:
            self.current_json_loader_thread.finished.connect(self.current_json_loader_thread.deleteLater)
            self.current_json_loader_thread.finished.connect(self.__on_json_loader_thread_finished)
            self.current_json_loader_thread.quit()
        if self.current_json_loader_worker:
            self.current_json_loader_worker.deleteLater()

    def __on_json_loader_thread_finished(self):
        self.current_json_loader_thread = None
        self.current_json_loader_worker = None

    def __handle_worker_error(self, error_msg):
        self.on_load_error.emit(error_msg)
        self.__handle_json_loader_worker_finished()