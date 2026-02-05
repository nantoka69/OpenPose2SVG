from model import file_loader, json_parser, svg_renderer
from .main_viewmodel import MainViewModel

# Instantiate the ViewModel with its dependencies when the module is loaded
main_viewmodel = MainViewModel(file_loader, json_parser, svg_renderer)
