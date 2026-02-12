from enum import Enum, auto

class ProcessingState(Enum):
    APP_START = auto()
    LOADING_FILE = auto()
    RENDERING = auto()
    FINISHED = auto()
    SAVING_SVG = auto()
    ERROR = auto()
