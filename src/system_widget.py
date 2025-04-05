import sys
import psutil
import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QMenu,
    QSystemTrayIcon,
    QStyle,
    QInputDialog,
    QColorDialog,
    QPushButton,
    QTabWidget,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSettings, QEvent, QProcess
from PyQt6.QtGui import QColor, QPalette, QContextMenuEvent, QAction, QMouseEvent, QIcon, QFontMetrics

# --- Configuration ---
UPDATE_INTERVAL_MS = 2000
TEXT_COLOR = "white"
DEFAULT_CORNER = "top-left"
CORNER_MARGIN = 10
LABEL_HEIGHT = 20
WIDGET_WIDTH = 250
LABEL_PADDING = 5
# --- End Configuration ---


class SystemMonitorWidget(QWidget):
    """
    A frameless, transparent widget to display CPU and Memory usage,
    positioned in a screen corner, with user-selectable corner and settings persistence.
    """

    def __init__(self):
        super().__init__()
        self.old_pos = None

        # --- Settings ---
        self.settings = QSettings("MyApplication", "SystemMonitorWidget")
        self.load_settings()  # Load settings

        # --- Window Setup ---
        self.setup_window()
        self.create_ui_elements()

        # --- Initial Positioning ---
        self.position_in_corner()

        # --- Timer for Updates ---
        self.start_timer()
        self.update_stats()

    def load_settings(self):
        """Loads settings from QSettings."""
        self.current_corner = self.settings.value("corner", DEFAULT_CORNER)
        if self.current_corner not in ["top-left", "top-right"]:
            self.current_corner = DEFAULT_CORNER

        self.widget_width = self.settings.value("widget_width", WIDGET_WIDTH)
        if not isinstance(self.widget_width, int):
            self.widget_width = WIDGET_WIDTH

        self.update_interval_ms = int(self.settings.value("update_interval_ms", UPDATE_INTERVAL_MS))
        self.text_color = str(self.settings.value("text_color", TEXT_COLOR))
        self.corner_margin = int(self.settings.value("corner_margin", CORNER_MARGIN))
        self.label_height = int(self.settings.value("label_height", LABEL_HEIGHT))
        self.label_padding = int(self.settings.value("label_padding", LABEL_PADDING))

    def setup_window(self):
        """Sets up the main window properties."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.installEventFilter(self)  # Event filter for context menu

    def create_ui_elements(self):
        """Creates and configures the UI elements (labels)."""
        self.mem_label = QLabel("MEM: --%", self)
        self.cpu_label = QLabel("CPU: --%", self)
        self.update_text_color()

        font = self.cpu_label.font()
        font.setPointSize(12)
        self.cpu_label.setFont(font)
        self.mem_label.setFont(font)

    def position_in_corner(self):
        """
        Calculates and sets the initial position of the widget,
        respecting the stored corner preference, applying CORNER_MARGIN,
        and aligning content to the screen edge using absolute positioning.
        """
        try:
            screen_geometry = QApplication.primaryScreen().availableGeometry()

            # Calculate widget dimensions
            widget_height = int(self.label_height) * 2 + 10

            self.resize(self.widget_width, widget_height)

            pos_x = 0
            pos_y = screen_geometry.top() + int(self.corner_margin)

            if self.current_corner == "top-right":
                pos_x = screen_geometry.right() - int(self.widget_width) - int(
                    self.corner_margin
                )
                self.mem_label.move(
                    int(self.widget_width) - self.mem_label.width() - int(self.corner_margin), 5
                )
                self.cpu_label.move(
                    int(self.widget_width) - self.cpu_label.width() - int(self.corner_margin),
                    int(self.label_height) + 5,
                )
            elif self.current_corner == "top-left":
                pos_x = screen_geometry.left() + int(self.corner_margin)
                self.mem_label.move(int(self.corner_margin), 5)
                self.cpu_label.move(int(self.corner_margin), int(self.label_height) + 5)
            else:
                print("Warning: Invalid corner setting. Defaulting to top-left.")
                pos_x = screen_geometry.left() + int(self.corner_margin)
                self.mem_label.move(int(self.corner_margin), 5)
                self.cpu_label.move(int(self.corner_margin), int(self.label_height) + 5)

            pos_x = max(screen_geometry.left(), pos_x)
            pos_y = max(screen_geometry.top(), pos_y)

            self.move(pos_x, pos_y)

        except Exception as e:
            print(f"Error positioning widget: {e}")
            self.move(50, 50)

    def start_timer(self):
        """Starts the timer for updating stats."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.update_interval_ms)

    def update_stats(self):
        """
        Fetches CPU and Memory usage and updates the labels.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()
            mem_usage = mem_info.percent
            mem_total = mem_info.total
            mem_used = mem_info.used

            # Format memory usage as string
            mem_str = (
                f"MEM: {mem_usage:.1f}% ({self.format_bytes(mem_used)} / {self.format_bytes(mem_total)})"
            )

            self.mem_label.setText(mem_str)
            self.cpu_label.setText(f"CPU: {cpu_usage:.1f}%")

        except Exception as e:
            print(f"Error updating stats: {e}")

    def format_bytes(self, bytes, decimals=1):
        """
        Helper function to format bytes into human-readable units.
        """
        KB = 1024
        MB = KB * 1024
        GB = MB * 1024

        if bytes < KB:
            return f"{bytes} B"
        elif bytes < MB:
            return f"{bytes / KB:.{decimals}f} KB"
        elif bytes < GB:
            return f"{bytes / MB:.{decimals}f} GB"
        else:
            return f"{bytes / GB:.{decimals}f} GB"

    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Handles right-click events to show a context menu,
        including options to change various settings.
        """
        context_menu = QMenu(self)

        # --- Settings Options ---
        config_action = QAction("Open Settings", self)
        config_action.triggered.connect(self.open_settings_window)
        context_menu.addAction(config_action)

        # --- Close Action ---
        close_action = QAction("Close Widget", self)
        close_action.triggered.connect(self.close)
        context_menu.addAction(close_action)

        context_menu.exec(event.globalPos())

    def mousePressEvent(self, event: QMouseEvent):
        """
        Captures mouse press events to initiate dragging.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Moves the window when the mouse is dragged.
        """
        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Resets the drag position when the mouse button is released.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None
            event.accept()

    def open_settings_window(self):
        """
        Opens a separate window to display and modify widget settings,
        organized into tabs.
        """
        self.settings_process = QProcess()
        self.settings_process.start("python", ["settings_app.py"])  # Adjust path if needed
        self.settings_process.finished.connect(self.read_settings)

    def read_settings(self):
        """
        Reads the settings from QSettings (or a file) after the settings process finishes.
        """
        temp_settings = QSettings("SettingsApp", "TempSettings")  # Same scope as settings_app
        self.update_interval_ms = int(temp_settings.value("update_interval_ms", 2000))
        self.corner_margin = int(temp_settings.value("corner_margin", 10))
        self.widget_width = int(temp_settings.value("widget_width", 250))
        self.label_height = int(temp_settings.value("label_height", 20))
        self.label_padding = int(temp_settings.value("label_padding", 5))
        self.text_color = str(temp_settings.value("text_color", "white"))
        self.current_corner = str(temp_settings.value("corner", "top-left"))

        self.settings.setValue("update_interval_ms", self.update_interval_ms)
        self.settings.setValue("corner_margin", self.corner_margin)
        self.settings.setValue("widget_width", self.widget_width)
        self.settings.setValue("label_height", self.label_height)
        self.settings.setValue("label_padding", self.label_padding)
        self.settings.setValue("text_color", self.text_color)
        self.settings.setValue("corner", self.current_corner)

        self.timer.start(self.update_interval_ms)
        self.position_in_corner()
        self.update_text_color()

    def set_top_left(self):
        """
        Sets the widget's corner to top-left and repositions it.
        """
        self.current_corner = "top-left"
        self.settings.setValue("corner", self.current_corner)
        self.position_in_corner()

    def set_top_right(self):
        """
        Sets the widget's corner to top-right and repositions it.
        """
        self.current_corner = "top-right"
        self.settings.setValue("corner", self.current_corner)
        self.position_in_corner()

    def set_widget_width(self):
        """
        Allows the user to set the widget's width.
        """
        width, ok = QInputDialog.getInt(self, "Set Width", "Enter widget width:", int(self.widget_width))
        if ok:
            self.widget_width = width
            self.settings.setValue("widget_width", self.widget_width)
            self.position_in_corner()  # Reposition and resize

    def set_update_interval(self):
        """
        Allows the user to set the update interval.
        """
        interval, ok = QInputDialog.getInt(self, "Set Update Interval", "Enter update interval (ms):", int(self.update_interval_ms))
        if ok:
            self.update_interval_ms = interval
            self.settings.setValue("update_interval_ms", self.update_interval_ms)
            self.timer.start(self.update_interval_ms)

    def set_text_color(self):
        """
        Allows the user to set the text color using a QColorDialog.
        """
        initial_color = QColor(self.text_color)  # Start with the current color
        color = QColorDialog.getColor(initial_color, self, "Set Text Color")
        if color.isValid():
            self.text_color = color.name()  # Get the color's name (e.g., #RRGGBB)
            self.settings.setValue("text_color", self.text_color)
            self.update_text_color()

    def set_corner_margin(self):
        """
        Allows the user to set the corner margin.
        """
        margin, ok = QInputDialog.getInt(self, "Set Corner Margin", "Enter corner margin (pixels):", int(self.corner_margin))
        if ok:
            self.corner_margin = margin
            self.settings.setValue("corner_margin", self.corner_margin)
            self.position_in_corner()  # Reposition

    def set_label_height(self):
        """
        Allows the user to set the label height.
        """
        height, ok = QInputDialog.getInt(self, "Set Label Height", "Enter label height (pixels):", int(self.label_height))
        if ok:
            self.label_height = height
            self.settings.setValue("label_height", self.label_height)
            self.position_in_corner()  # Reposition and resize

    def set_label_padding(self):
        """
        Allows the user to set the label padding.
        """
        padding, ok = QInputDialog.getInt(self, "Set Label Padding", "Enter label padding (pixels):", int(self.label_padding))
        if ok:
            self.label_padding = padding
            self.settings.setValue("label_padding", self.label_padding)
            self.position_in_corner()

    def update_text_color(self):
        """
        Updates the text color of the labels.
        """
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.text_color))
        self.cpu_label.setPalette(palette)
        self.mem_label.setPalette(palette)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.Type.ContextMenu:
            self.contextMenuEvent(event)  # Call your existing contextMenuEvent
            return True  # Indicate that you've handled the event
        return super().eventFilter(obj, event)

class SystemTrayIcon(QSystemTrayIcon):
    """
    Manages the system tray icon and its context menu.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.show_action = None
        self.hide_action = None
        self.widget = parent

        self.setIcon(QIcon("assets/icon.ico"))
        self.setToolTip("System Monitor")

        self.menu = QMenu()
        self.show_action = self.menu.addAction("Show")
        self.hide_action = self.menu.addAction("Hide")
        self.quit_action = self.menu.addAction("Quit")

        self.show_action.triggered.connect(self.show_widget)
        self.hide_action.triggered.connect(self.hide_widget)
        self.quit_action.triggered.connect(self.quit_app)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_icon_activated)

        self.show()

        # Initialize the tray icon *after* the main widget is set up
        # self.tray_icon = SystemTrayIcon(self)

    def show_widget(self):
        """
        Shows the main widget.
        """
        self.widget.show()

    def hide_widget(self):
        """
        Hides the main widget.
        """
        self.widget.hide()

    def quit_app(self):
        """
        Quits the application and its processes.
        """
        QApplication.quit()

    def on_tray_icon_activated(self, reason):
        """
        Handles clicks on the system tray icon.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.widget.isVisible():
                self.hide_widget()
            else:
                self.show_widget()

# --- Main Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = SystemMonitorWidget()
    tray_icon = SystemTrayIcon(widget)

    widget.show()

    sys.exit(app.exec())