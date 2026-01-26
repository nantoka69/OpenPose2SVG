from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QPlainTextEdit, QScrollArea, QLabel, QSplitter, QSizePolicy, QFrame,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from viewmodel.main_viewmodel import ViewModelError

class ViewError(Exception):
    """Generic exception for the view layer."""
    pass

class MainWindow(QMainWindow):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("OpenPose2SVG")
        self.setMinimumSize(400, 300)
        self.resize(1200, 800)
        
        # Main central widget and vertical layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        self.setCentralWidget(central_widget)
        
        # Splitter for the two halves
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(2) # Thin line
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #444;
            }
        """)
        
        # --- Left Side: JSON Text Area ---
        self.json_text_edit = QPlainTextEdit()
        self.json_text_edit.setReadOnly(True)
        self.json_text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.json_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.json_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # --- Right Side: Pixel Graphic Area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel("Graphic Preview Area")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        
        # Add widgets directly to splitter
        self.splitter.addWidget(self.json_text_edit)
        self.splitter.addWidget(self.scroll_area)
        
        # Set equal initial sizing for splitter
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        # Force initial sizes to be non-zero
        self.splitter.setSizes([595, 595]) 
        
        # Prevent panels from being collapsed (this stops the handle at the minimum size)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        
        # Ensure splitter takes all available vertical space
        main_layout.addWidget(self.splitter, 1)
        
        # --- Bottom Bar with Buttons ---
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        # Left area for "Load JSON" button
        self.left_btn_container = QWidget()
        self.left_btn_layout = QHBoxLayout(self.left_btn_container)
        self.left_btn_layout.setContentsMargins(0, 5, 0, 5)
        self.load_json_button = QPushButton("Load JSON")
        self.load_json_button.setStyleSheet("font-size: 18px; padding: 5px 15px;")
        self.left_btn_layout.addStretch()
        self.left_btn_layout.addWidget(self.load_json_button)
        self.left_btn_layout.addStretch()
        
        # Settings button (symbol only)
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedWidth(50)
        self.settings_button.setStyleSheet("font-size: 24px; border: none;")
        self.settings_button.setFlat(True)
        
        # Right area for "Save SVG" button
        self.right_btn_container = QWidget()
        self.right_btn_layout = QHBoxLayout(self.right_btn_container)
        self.right_btn_layout.setContentsMargins(0, 5, 0, 5)
        self.save_svg_button = QPushButton("Save SVG")
        self.save_svg_button.setStyleSheet("font-size: 18px; padding: 5px 15px;")
        self.right_btn_layout.addStretch()
        self.right_btn_layout.addWidget(self.save_svg_button)
        self.right_btn_layout.addStretch()
        
        bottom_layout.addWidget(self.left_btn_container)
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.right_btn_container)
        
        main_layout.addWidget(bottom_container)

        # Set minimum sizes for panels based on buttons
        # We add a buffer to ensure the settings button (50px) has enough space centered on the handle
        btn_min_width = self.load_json_button.sizeHint().width() + 20
        # The container width must be at least btn_min, but the panel in the splitter
        # should also account for the fact that the settings button overlaps it.
        panel_min = btn_min_width + 25 # settings_width // 2
        
        self.json_text_edit.setMinimumWidth(panel_min)
        self.scroll_area.setMinimumWidth(panel_min)
        
        # Update button alignment when splitter moves
        self.splitter.splitterMoved.connect(self.update_bottom_alignment)
        
        # Connect signals
        self.load_json_button.clicked.connect(self.on_load_json_clicked)
        self.save_svg_button.clicked.connect(self.on_save_svg_clicked)
        
        # Use QTimer to ensure alignment happens after the layout is calculated
        QTimer.singleShot(0, self.update_bottom_alignment)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Use QTimer to decouple resize from layout calculation to prevent feedback loops
        QTimer.singleShot(0, self.update_bottom_alignment)

    def update_bottom_alignment(self):
        # Synchronize bottom containers with splitter panels
        sizes = self.splitter.sizes()
        if not sizes or sum(sizes) == 0:
            # If sizes are not yet available, use half the window width as a fallback
            w = self.width() // 2
            sizes = [w, w]
            
        left_width = sizes[0]
        right_width = sizes[1]
        handle_width = self.splitter.handleWidth()
        settings_width = self.settings_button.width()
        
        # Offset to center settings button on the splitter handle
        offset = (settings_width - handle_width) // 2
        
        # Set widths precisely
        self.left_btn_container.setFixedWidth(max(0, left_width - offset))
        self.right_btn_container.setFixedWidth(max(0, right_width - offset))

    def on_load_json_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                self.load_file_with_handling(file_path)
            except ViewError as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_file_with_handling(self, file_path):
        """Helper method to handle the rethrowing logic as requested."""
        try:
            content = self.viewmodel.load_json(file_path)
            self.json_text_edit.setPlainText(content)
        except ViewModelError as e:
            # Rethrow as ViewError as per the "generic exception" request
            raise ViewError(str(e))

    def on_save_svg_clicked(self):
        print("Save SVG clicked")
