from PyQt6.QtCore import QObject, pyqtSignal, QThread
from .load_open_point_data_worker import LoadOpenPointDataWorker
from .processing_state import ProcessingState

from .error import ViewModelError

class MainViewModel(QObject):
    # Signals for View Layer
    on_json_loaded = pyqtSignal(str)
    on_load_error = pyqtSignal(str)
    on_state_changed = pyqtSignal(ProcessingState)

    def __init__(self, file_loader, json_parser):
        super().__init__()
        self.file_loader = file_loader
        self.json_parser = json_parser
        self.current_json_loader_thread = None
        self.current_json_loader_worker = None
        self.on_state_changed.emit(ProcessingState.APP_START)
        
    def load_json(self, file_path):
        print(f"[ViewModel] Transitioning to LOADING_FILE for: {file_path}")
        self.on_state_changed.emit(ProcessingState.LOADING_FILE)
        self.__stop_existing_thread_if_any()

        self.current_json_loader_thread = QThread()
        self.current_json_loader_worker = LoadOpenPointDataWorker(file_path, self.file_loader, self.json_parser)
        
        self.current_json_loader_worker.moveToThread(self.current_json_loader_thread)
        
        self.__connect_signals()
        
        self.current_json_loader_thread.start()

    def __handle_json_loaded(self, pretty_json):
        print("[ViewModel] JSON loaded successfully")
        self.on_json_loaded.emit(pretty_json)

    def __handle_rendering_started(self):
        print("[ViewModel] Transitioning to RENDERING")
        self.on_state_changed.emit(ProcessingState.RENDERING)

    def __handle_json_loader_worker_finished(self, emit_state=True):
        if self.current_json_loader_thread:
            self.current_json_loader_thread.quit()
        
        if self.current_json_loader_worker:
            self.current_json_loader_worker.deleteLater()
            
        if emit_state:
            print("[ViewModel] Transitioning to FINISHED")
            self.on_state_changed.emit(ProcessingState.FINISHED)

    def __on_json_loader_thread_finished(self):
        self.current_json_loader_thread = None
        self.current_json_loader_worker = None

    def __handle_worker_error(self, error_msg):
        self.on_state_changed.emit(ProcessingState.ERROR)
        self.on_load_error.emit(error_msg)
        self.__handle_json_loader_worker_finished(emit_state=False)

    def __stop_existing_thread_if_any(self):
        if self.current_json_loader_thread:
            if self.current_json_loader_thread.isRunning():
                self.current_json_loader_thread.quit()
            self.current_json_loader_thread.wait()
            self.current_json_loader_thread = None
            self.current_json_loader_worker = None

    def __connect_signals(self):
        self.current_json_loader_thread.started.connect(self.current_json_loader_worker.run)
        self.current_json_loader_worker.rendering_started.connect(self.__handle_rendering_started)
        self.current_json_loader_worker.json_loaded.connect(self.__handle_json_loaded)
        self.current_json_loader_worker.finished.connect(self.__handle_json_loader_worker_finished)
        self.current_json_loader_worker.error.connect(self.__handle_worker_error)
        
        print(f"[ViewModel] Signals connected for worker {self.current_json_loader_worker}")