from model.file_loader import FileLoader, ModelError
from model.json_parser import PoseJsonParser, ParserError

class ViewModelError(Exception):
    """Generic exception for the viewmodel layer."""
    pass

class MainViewModel:
    def __init__(self, file_loader, json_parser):
        self.file_loader = file_loader
        self.json_parser = json_parser
        
    def load_json(self, file_path):
        try:
            content = self.file_loader.load_text_file(file_path)
            # Parse the content to ensure it's valid JSON and get pretty string
            self.current_pose_data, pretty_json = self.json_parser.parse_pose_json(content)
            
            print(f"Loading and parsing JSON from: {file_path}")
            return pretty_json
        except (ModelError, ParserError) as e:
            raise ViewModelError(str(e))
        except Exception as e:
            raise ViewModelError(f"Unexpected error in ViewModel: {str(e)}")


