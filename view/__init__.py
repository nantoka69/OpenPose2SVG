from viewmodel import main_viewmodel
from .main_window import MainWindow

# Instantiate the MainWindow with dependencies
# NOTE: QApplication must be created before importing this module
main_window = MainWindow(main_viewmodel)
