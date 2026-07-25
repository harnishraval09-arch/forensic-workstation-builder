"""
Settings page
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QFrame, QFileDialog, QPushButton
)
from PySide6.QtCore import QSettings, Signal  # ← ADDED Signal here
from pathlib import Path

from ..theme import set_theme

class SettingsPage(QWidget):
    theme_changed = Signal(str)
    
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(24)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 600; color: #ffffff;")
        layout.addWidget(title)
        
        # Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #141414;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        
        # Theme
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet("color: #8e8e93; font-size: 13px;")
        container_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8e8e93;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
        """)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        container_layout.addWidget(self.theme_combo)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #2a2a2a; max-height: 1px; margin: 8px 0;")
        container_layout.addWidget(sep)
        
        # Log level
        log_label = QLabel("Log Level")
        log_label.setStyleSheet("color: #8e8e93; font-size: 13px;")
        container_layout.addWidget(log_label)
        
        self.log_combo = QComboBox()
        self.log_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8e8e93;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #141414;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
        """)
        container_layout.addWidget(self.log_combo)
        
        layout.addWidget(container)
        layout.addStretch()
    
    def load_settings(self):
        settings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")
        theme = settings.value("theme", "dark")
        self.theme_combo.setCurrentText("Dark" if theme == "dark" else "Light")
    
    def on_theme_changed(self, theme_name):
        theme = "dark" if theme_name == "Dark" else "light"
        set_theme(theme)
        self.theme_changed.emit(theme)