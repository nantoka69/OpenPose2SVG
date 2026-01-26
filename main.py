from PyQt6.QtWidgets import QApplication
import sys
from view.main_window import MainWindow
from viewmodel.main_viewmodel import MainViewModel

def main():
    app = QApplication(sys.argv)
    
    # Initialize components
    viewmodel = MainViewModel()
    window = MainWindow(viewmodel)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
