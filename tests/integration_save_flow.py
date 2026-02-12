import sys
import os
import time
from PyQt6.QtCore import QCoreApplication, QTimer

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from viewmodel.main_viewmodel import MainViewModel
from model.file_handler import FileHandler
from model.json_parser import PoseJsonParser
from viewmodel.processing_state import ProcessingState

def test_full_save_flow():
    app = QCoreApplication(sys.argv)
    
    file_handler = FileHandler()
    json_parser = PoseJsonParser()
    viewmodel = MainViewModel(file_handler, json_parser)
    
    test_file = "integration_save.svg"
    test_content = "<svg>Integration Test</svg>"
    
    states_visited = []
    
    def on_state_changed(state):
        print(f"State changed to: {state}")
        states_visited.append(state)
        if state == ProcessingState.FINISHED and ProcessingState.SAVING_SVG in states_visited:
            print("Finished state reached after saving!")
            app.quit()

    viewmodel.on_state_changed.connect(on_state_changed)
    
    print("Starting save_svg integration test...")
    viewmodel.save_svg(test_file, test_content)
    
    # Timeout after 5 seconds
    QTimer.singleShot(5000, lambda: (print("Test timed out!"), app.quit()))
    
    app.exec()
    
    assert ProcessingState.SAVING_SVG in states_visited
    assert ProcessingState.FINISHED in states_visited
    assert os.path.exists(test_file)
    
    with open(test_file, 'r') as f:
        assert f.read() == test_content
        
    os.remove(test_file)
    print("Integration test passed successfully!")

if __name__ == "__main__":
    test_full_save_flow()
