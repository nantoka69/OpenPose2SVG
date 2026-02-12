from model import file_handler, json_parser
from .main_viewmodel import MainViewModel

# Instantiate the ViewModel with its dependencies when the module is loaded
main_viewmodel = MainViewModel(file_handler, json_parser)
