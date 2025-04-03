import sys
import psutil # Library to get system info (CPU, RAM)
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QMenu)
from PyQt6.QtCore import (Qt, QTimer, QPoint)
from PyQt6.QtGui import (QColor, QPalette, QContextMenuEvent, QAction, QMouseEvent)

# --- Configuration ---
UPDATE_INTERVAL_MS = 2000  # How often to update stats (in milliseconds). 2000ms = 2 seconds.
TEXT_COLOR = "white"      # Default text color (e.g., "white", "black", "#FF0000")
# NEW: Choose initial corner: "top-right" or "top-left"
DEFAULT_CORNER = "top-right"
CORNER_MARGIN = 10 # Pixels margin from the screen edge
# --- End Configuration ---

class SystemMonitorWidget(QWidget):
    """
    A frameless, transparent widget to display CPU and Memory usage,
    positioned in a screen corner.
    """
    def __init__(self):
        super().__init__()
        self.old_pos = None # To store mouse position for dragging

        # --- Window Setup ---
        # Make the window frameless and potentially skip taskbar (Tool)
        # REMOVED: Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # No window border, title bar, etc.
            Qt.WindowType.Tool                        # Try to prevent appearing in the taskbar
        )
        # Make the window background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # --- UI Elements ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Add some padding around text

        self.cpu_label = QLabel("CPU: --%")
        self.mem_label = QLabel("MEM: --%")

        # Set text color
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_COLOR))
        self.cpu_label.setPalette(palette)
        self.mem_label.setPalette(palette)
        # Optionally set font size
        font = self.cpu_label.font()
        font.setPointSize(12) # Adjust font size as needed
        self.cpu_label.setFont(font)
        self.mem_label.setFont(font)

        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.mem_label)
        self.setLayout(self.layout)

        # Adjust initial size based on content BEFORE calculating position
        self.adjustSize() # More reliable than resize(sizeHint()) before showing

        # --- Initial Positioning ---
        self.position_in_corner()

        # --- Timer for Updates ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(UPDATE_INTERVAL_MS) # Start timer with configured interval

        # Initial update
        self.update_stats()

    def position_in_corner(self):
        """
        Calculates and sets the initial position of the widget based on
        DEFAULT_CORNER setting.
        """
        try:
            # Get available screen geometry (excludes taskbar)
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            widget_size = self.size() # Get current size after adjustSize()

            pos_x = 0
            pos_y = screen_geometry.top() + CORNER_MARGIN # Start Y at the top margin

            if DEFAULT_CORNER == "top-right":
                # Calculate X for top-right corner
                pos_x = screen_geometry.right() - widget_size.width() - CORNER_MARGIN
            elif DEFAULT_CORNER == "top-left":
                # Calculate X for top-left corner
                pos_x = screen_geometry.left() + CORNER_MARGIN
            else:
                # Default to top-left if setting is invalid
                print(f"Warning: Invalid DEFAULT_CORNER '{DEFAULT_CORNER}'. Defaulting to top-left.")
                pos_x = screen_geometry.left() + CORNER_MARGIN

            # Ensure position is not negative (can happen on multi-monitor setups sometimes)
            pos_x = max(screen_geometry.left(), pos_x)
            pos_y = max(screen_geometry.top(), pos_y)

            self.move(pos_x, pos_y) # Move the widget to the calculated position

        except Exception as e:
            print(f"Error positioning widget: {e}")
            # Fallback: just place it near the top-left if screen detection fails
            self.move(50, 50)

    def update_stats(self):
        """
        Fetches CPU and Memory usage and updates the labels.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()
            mem_usage = mem_info.percent

            self.cpu_label.setText(f"CPU: {cpu_usage:.1f}%")
            self.mem_label.setText(f"MEM: {mem_usage:.1f}%")

            # Optional: Adjust size dynamically if needed, but might cause movement
            # self.adjustSize()

        except Exception as e:
            print(f"Error updating stats: {e}")
            # self.cpu_label.setText("CPU: Error")
            # self.mem_label.setText("MEM: Error")

    # --- Window Interaction ---
    # (contextMenuEvent, mousePressEvent, mouseMoveEvent, mouseReleaseEvent remain the same)
    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Handles right-click events to show a context menu.
        """
        context_menu = QMenu(self)
        close_action = QAction("Close Widget", self)
        close_action.triggered.connect(self.close) # Connect action to close method
        context_menu.addAction(close_action)
        context_menu.exec(event.globalPos()) # Show menu at mouse cursor position

    def mousePressEvent(self, event: QMouseEvent):
        """
        Captures mouse press events to initiate dragging.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint() # Store click position
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Moves the window when the mouse is dragged (if left button is held).
        """
        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Resets the drag position when the mouse button is released.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None
            event.accept()


# --- Main Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Optional Style Sheet (keep commented out unless needed)
    # app.setStyleSheet(...)

    widget = SystemMonitorWidget()
    widget.show()

    sys.exit(app.exec())
