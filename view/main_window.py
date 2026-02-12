from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QPlainTextEdit, QScrollArea, QLabel, QSplitter, QSizePolicy, QFrame,
    QFileDialog, QMessageBox, QApplication
)
import sys
from PyQt6.QtCore import Qt, QTimer, QByteArray, QRectF
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from viewmodel.error import ViewModelError
from viewmodel.processing_state import ProcessingState

class ViewError(Exception):
    """Generic exception for the view layer."""
    pass

class MainWindow(QMainWindow):
    def __init__(self, viewmodel):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        super().__init__()
        self.viewmodel = viewmodel
        self.current_svg_content = None # Store SVG for re-rendering on resize
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
        
        self.load_json_button.clicked.connect(self.on_load_json_clicked)
        self.save_svg_button.clicked.connect(self.on_save_svg_clicked)
        
        self.splitter.splitterMoved.connect(self.update_bottom_alignment)
        self.splitter.splitterMoved.connect(lambda: QTimer.singleShot(10, self._render_svg))

        # Connect ViewModel signals
        self.viewmodel.on_json_loaded.connect(self.on_json_loaded)
        self.viewmodel.on_load_error.connect(self.on_load_error)
        self.viewmodel.on_svg_ready.connect(self.on_svg_ready)
        self.viewmodel.on_state_changed.connect(self.on_processing_state_changed)
        
        # Initialize UI state
        self.on_processing_state_changed(ProcessingState.APP_START)
        
        # Use QTimer to ensure alignment happens after the layout is calculated
        QTimer.singleShot(0, self.update_bottom_alignment)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Use QTimer to decouple resize from layout calculation to prevent feedback loops
        QTimer.singleShot(0, self.update_bottom_alignment)
        # Re-render SVG to fit new size, slightly delayed to let layout settle
        QTimer.singleShot(10, self._render_svg)

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
            self.viewmodel.load_json(file_path)

    def on_json_loaded(self, content):
        self.json_text_edit.setPlainText(content)

    def on_load_error(self, error_msg):
        # Do not clear the JSON text edit to preserve the last successful load
        QMessageBox.critical(self, "Error", error_msg)

    def on_save_svg_clicked(self):
        if not self.current_svg_content:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save SVG File",
            "pose.svg",
            "SVG Files (*.svg);;All Files (*)"
        )
        if file_path:
            self.viewmodel.save_svg(file_path, self.current_svg_content)

    def on_svg_ready(self, svg_content):
        print("[View] SVG content received")
        self.current_svg_content = svg_content
        self._render_svg()

    def _render_svg(self):
        if not self.current_svg_content:
            return
            
        print("[View] Rendering SVG to viewport size (preserving aspect ratio)...")
        
        # Use viewport size instead of label size for more reliable dimensions
        viewport_size = self.scroll_area.viewport().size()
        
        # Use a small buffer to ensure we don't trigger scrollbars
        w = max(10, viewport_size.width() - 2)
        h = max(10, viewport_size.height() - 2)
            
        # Create a renderer from the SVG string
        renderer = QSvgRenderer(QByteArray(self.current_svg_content.encode('utf-8')))
        
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        
        # Calculate aspect ratio preserving rectangle
        svg_size = renderer.defaultSize()
        if svg_size.isValid():
            # Calculate the scale factor
            target_rect = QRectF(0, 0, w, h)
            aspect_ratio = svg_size.width() / svg_size.height()
            
            if w / h > aspect_ratio:
                # Viewport is wider than SVG - scale by height
                new_w = h * aspect_ratio
                target_rect.setX((w - new_w) / 2)
                target_rect.setWidth(new_w)
            else:
                # Viewport is taller than SVG - scale by width
                new_h = w / aspect_ratio
                target_rect.setY((h - new_h) / 2)
                target_rect.setHeight(new_h)
            
            renderer.render(painter, target_rect)
        else:
            # Fallback if svg size is invalid
            renderer.render(painter)
            
        painter.end()
        
        # Display the pixmap
        self.image_label.setPixmap(pixmap)
        print(f"[View] SVG rendered onto label (aspect ratio preserved) with size {w}x{h}")

    def on_processing_state_changed(self, state):
        now = __import__('time').time()
        print(f"[View] ({now:.3f}) Received state change: {state}")
        # Update window title to reflect state for debugging
        self.setWindowTitle(f"OpenPose2SVG - [{state.name}]")
        
        if state == ProcessingState.APP_START:
            self.load_json_button.setEnabled(True)
            self.save_svg_button.setEnabled(False)
            self.image_label.setText("READY")
            self.image_label.setStyleSheet("color: #333;")
        elif state == ProcessingState.LOADING_FILE:
            self.load_json_button.setEnabled(False)
            self.save_svg_button.setEnabled(False)
            if self.current_svg_content is None:
                self.image_label.setText("LOADING FILE...")
                self.image_label.setStyleSheet("color: blue; font-size: 24px; font-weight: bold;")
        elif state == ProcessingState.RENDERING:
            self.load_json_button.setEnabled(False)
            self.save_svg_button.setEnabled(False)
            if self.current_svg_content is None:
                self.image_label.setText("RENDERING VISUALS...")
                self.image_label.setStyleSheet("color: red; font-size: 24px; font-weight: bold;")
        elif state == ProcessingState.SAVING_SVG:
            self.load_json_button.setEnabled(False)
            self.save_svg_button.setEnabled(False)
        elif state == ProcessingState.FINISHED:
            self.load_json_button.setEnabled(True)
            self.save_svg_button.setEnabled(self.current_svg_content is not None)
        elif state == ProcessingState.ERROR:
            self.load_json_button.setEnabled(True)
            self.save_svg_button.setEnabled(self.current_svg_content is not None)
            
            if self.current_svg_content is None:
                self.image_label.setText("ERROR OCCURRED")
                self.image_label.setStyleSheet("color: darkred;")
        
        # Force immediate refresh
        self.image_label.repaint()
        QApplication.instance().processEvents()
        print(f"[View] ({__import__('time').time():.3f}) UI updated for {state}")
