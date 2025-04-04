import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTabWidget,
                             QLabel, QLineEdit, QPushButton, QColorDialog,
                             QGridLayout, QHBoxLayout, QComboBox)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QColor, QPalette

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Settings")
        self.setGeometry(200, 200, 400, 300)

        self.settings = QSettings("SettingsApp", "TempSettings")

        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # --- General Tab ---
        general_tab = QWidget()
        general_layout = QGridLayout()

        # Update Interval
        interval_label = QLabel("Update Interval (ms):", general_tab)
        self.interval_input = QLineEdit(general_tab)
        self.interval_input.setText(str(self.settings.value("update_interval_ms", 2000)))
        general_layout.addWidget(interval_label, 0, 0)
        general_layout.addWidget(self.interval_input, 0, 1)

        # Corner Margin
        margin_label = QLabel("Corner Margin (pixels):", general_tab)
        self.margin_input = QLineEdit(general_tab)
        self.margin_input.setText(str(self.settings.value("corner_margin", 10)))
        general_layout.addWidget(margin_label, 1, 0)
        general_layout.addWidget(self.margin_input, 1, 1)

        # Widget Width
        width_label = QLabel("Widget Width (pixels):", general_tab)
        self.width_input = QLineEdit(general_tab)
        self.width_input.setText(str(self.settings.value("widget_width", 250)))
        general_layout.addWidget(width_label, 2, 0)
        general_layout.addWidget(self.width_input, 2, 1)

        # Label Height
        height_label = QLabel("Label Height (pixels):", general_tab)
        self.height_input = QLineEdit(general_tab)
        self.height_input.setText(str(self.settings.value("label_height", 20)))
        general_layout.addWidget(height_label, 3, 0)
        general_layout.addWidget(self.height_input, 3, 1)

        # Label Padding
        padding_label = QLabel("Label Padding (pixels):", general_tab)
        self.padding_input = QLineEdit(general_tab)
        self.padding_input.setText(str(self.settings.value("label_padding", 5)))
        general_layout.addWidget(padding_label, 4, 0)
        general_layout.addWidget(self.padding_input, 4, 1)

        # Corner Selection (QComboBox)
        corner_label = QLabel("Widget Corner:", general_tab)
        self.corner_combo = QComboBox(general_tab)
        self.corner_combo.addItems(["Top-Left", "Top-Right"])

        # Set the correct initial selection
        corner = self.settings.value("corner", "top-left")
        if corner == "top-right":
            self.corner_combo.setCurrentIndex(1)  # Index for "Top-Right"
        else:
            self.corner_combo.setCurrentIndex(0)  # Index for "Top-Left"

        general_layout.addWidget(corner_label, 5, 0)
        general_layout.addWidget(self.corner_combo, 5, 1)

        # Empty label for spacing
        empty_label = QLabel("", general_tab)
        general_layout.addWidget(empty_label, 6, 0, 1, 2)  # Span 2 columns

        general_tab.setLayout(general_layout)
        tab_widget.addTab(general_tab, "General")

        # --- Text Color Tab ---
        text_color_tab = QWidget()
        text_color_layout = QVBoxLayout()

        color_button = QPushButton("Select Text Color", text_color_tab)
        color_button.clicked.connect(self.set_text_color)
        self.color_preview = QLabel("", text_color_tab)
        self.update_color_preview()

        text_color_layout.addWidget(color_button)

        # Color preview layout
        color_preview_layout = QHBoxLayout()
        color_preview_layout.addWidget(self.color_preview)
        text_color_layout.addLayout(color_preview_layout)

        text_color_tab.setLayout(text_color_layout)
        tab_widget.addTab(text_color_tab, "Text Color")

        layout.addWidget(tab_widget)

        apply_button = QPushButton("Apply", self)
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)

        self.setLayout(layout)

        # Store input values as attributes
        self.interval = self.settings.value("update_interval_ms", 2000)
        self.margin = self.settings.value("corner_margin", 10)
        self.width = self.settings.value("widget_width", 250)
        self.height = self.settings.value("label_height", 20)
        self.padding = self.settings.value("label_padding", 5)
        self.color = self.settings.value("text_color", "white")

    def update_color_preview(self):
        """Updates the color preview label with the current text color."""
        color = self.settings.value("text_color", "white")
        self.color_preview.setStyleSheet(
            f"background-color: {color};"
            "height: 20px;"
            "width: 80px;"
        )
        self.color_preview.setFixedHeight(20)
        self.color_preview.setFixedWidth(80)

    def set_text_color(self):
        initial_color = QColor(self.settings.value("text_color", "white"))
        color = QColorDialog.getColor(initial_color, self, "Select Text Color")
        if color.isValid():
            self.settings.setValue("text_color", color.name())
            self.update_color_preview()
            self.color = color.name()

    def apply_settings(self):
        # Update settings and attributes
        self.settings.setValue("update_interval_ms", int(self.interval_input.text()))
        self.settings.setValue("corner_margin", int(self.margin_input.text()))
        self.settings.setValue("widget_width", int(self.width_input.text()))
        self.settings.setValue("label_height", int(self.height_input.text()))
        self.settings.setValue("label_padding", int(self.padding_input.text()))
        self.settings.setValue("text_color", self.color)

        # Determine the selected corner
        corner = "top-left" if self.corner_combo.currentIndex() == 0 else "top-right"
        self.settings.setValue("corner", corner)

        # Emit a signal or use a mechanism to notify the main app
        # For simplicity, we'll just save to QSettings and assume the main app
        # will read it when needed. A signal/slot mechanism would be better.
        self.settings.sync()
        self.close()

    def closeEvent(self, event):
        """Override closeEvent to handle window closing."""
        self.apply_settings()  # Apply settings before closing
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())