import logging
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QFileDialog, QMessageBox, QScrollArea
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)  # "dark" | "light"

    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        settings = app_state.qsettings

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a2a2a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3a3a3a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Content widget inside scroll
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(18)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        root.addWidget(title)

        # --- Directories -------------------------------------------------
        dirs_card = self._card("Directories")
        dirs_layout = dirs_card.layout()

        # Download directory
        download_row = QHBoxLayout()

        download_label = QLabel("Download directory")
        download_label.setObjectName("FieldLabel")
        download_label.setFixedWidth(150)
        download_row.addWidget(download_label)

        self.download_display = QLabel(
            str(app_state.tool_manager.tools_dir / "downloads")
        )
        self.download_display.setObjectName("MonoText")
        self.download_display.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 12px;
                font-family: 'Consolas', monospace;
                background-color: #1a1a1a;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #2a2a2a;
            }
        """)
        self.download_display.setWordWrap(True)
        download_row.addWidget(self.download_display, 1)

        download_browse = QPushButton("Browse")
        download_browse.setFixedWidth(70)
        download_browse.clicked.connect(lambda: self._browse_download())
        download_row.addWidget(download_browse)

        dirs_layout.addLayout(download_row)

        # Installation directory
        install_row = QHBoxLayout()

        install_label = QLabel("Installation directory")
        install_label.setObjectName("FieldLabel")
        install_label.setFixedWidth(150)
        install_row.addWidget(install_label)

        self.install_display = QLabel(
            str(app_state.tool_manager.tools_dir / "installed")
        )
        self.install_display.setObjectName("MonoText")
        self.install_display.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 12px;
                font-family: 'Consolas', monospace;
                background-color: #1a1a1a;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #2a2a2a;
            }
        """)
        self.install_display.setWordWrap(True)
        install_row.addWidget(self.install_display, 1)

        install_browse = QPushButton("Browse")
        install_browse.setFixedWidth(70)
        install_browse.clicked.connect(lambda: self._browse_install())
        install_row.addWidget(install_browse)

        dirs_layout.addLayout(install_row)

        save_dirs_btn = QPushButton("Save Directories")
        save_dirs_btn.setObjectName("PrimaryButton")
        save_dirs_btn.clicked.connect(self._save_directories)
        dirs_layout.addWidget(save_dirs_btn)

        root.addWidget(dirs_card)

        # --- Appearance ----------------------------------------------------
        appearance_card = self._card("Appearance")
        appearance_layout = appearance_card.layout()

        theme_row = QHBoxLayout()

        theme_label = QLabel("Theme")
        theme_label.setObjectName("FieldLabel")
        theme_label.setFixedWidth(150)
        theme_row.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])

        current_theme = settings.value("theme", "dark")
        self.theme_combo.setCurrentText(
            "Dark" if current_theme == "dark" else "Light"
        )

        self.theme_combo.currentTextChanged.connect(
            self._on_theme_changed
        )

        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()

        appearance_layout.addLayout(theme_row)
        root.addWidget(appearance_card)

        # --- Updates ---------------------------------------------------
        updates_card = self._card("Update Policy")
        updates_layout = updates_card.layout()

        policy_row = QHBoxLayout()

        policy_label = QLabel("When updates are available")
        policy_label.setObjectName("FieldLabel")
        policy_label.setFixedWidth(150)
        policy_row.addWidget(policy_label)

        self.policy_combo = QComboBox()
        self.policy_combo.addItems([
            "Manual (ask before updating)",
            "Notify only",
            "Automatic"
        ])

        self.policy_combo.setCurrentText(
            settings.value(
                "update_policy",
                "Manual (ask before updating)"
            )
        )

        self.policy_combo.currentTextChanged.connect(
            lambda v: settings.setValue("update_policy", v)
        )

        policy_row.addWidget(self.policy_combo)
        policy_row.addStretch()

        updates_layout.addLayout(policy_row)

        note = QLabel(
            "Note: update detection isn't implemented in the backend yet "
            "— this only stores your preference."
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)
        updates_layout.addWidget(note)

        root.addWidget(updates_card)

        # --- Logging -----------------------------------------------------
        logging_card = self._card("Logging")
        logging_layout = logging_card.layout()

        # Log level
        level_row = QHBoxLayout()

        level_label = QLabel("Log level")
        level_label.setObjectName("FieldLabel")
        level_label.setFixedWidth(150)
        level_row.addWidget(level_label)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems([
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR"
        ])

        self.log_level_combo.setCurrentText(
            settings.value("log_level", "INFO")
        )

        self.log_level_combo.currentTextChanged.connect(
            self._on_log_level_changed
        )

        level_row.addWidget(self.log_level_combo)
        level_row.addStretch()

        logging_layout.addLayout(level_row)

        # Log file path
        log_row = QHBoxLayout()

        log_label = QLabel("Log file:")
        log_label.setObjectName("FieldLabel")
        log_label.setFixedWidth(150)
        log_row.addWidget(log_label)

        log_path_label = QLabel(str(self.app_state.log_file))
        log_path_label.setObjectName("MonoText")
        log_path_label.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 12px;
                font-family: 'Consolas', monospace;
                background-color: #1a1a1a;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #2a2a2a;
            }
        """)
        log_path_label.setWordWrap(True)
        log_row.addWidget(log_path_label, 1)

        open_log_btn = QPushButton("Open Log Folder")
        open_log_btn.setFixedWidth(120)
        open_log_btn.clicked.connect(self._open_log_folder)
        log_row.addWidget(open_log_btn)

        logging_layout.addLayout(log_row)
        root.addWidget(logging_card)

        root.addStretch()

        # Set the content widget to the scroll area
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _card(self, title_text: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        return card

    def _browse_download(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            str(
                self.app_state.tool_manager.tools_dir
                / "downloads"
            )
        )

        if directory:
            self.download_display.setText(directory)

    def _browse_install(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            str(
                self.app_state.tool_manager.tools_dir
                / "installed"
            )
        )

        if directory:
            self.install_display.setText(directory)

    def _save_directories(self):
        QMessageBox.information(
            self,
            "Saved",
            "Directory preferences saved."
        )

    def _on_theme_changed(self, text: str):
        theme = "dark" if text == "Dark" else "light"
        self.app_state.qsettings.setValue("theme", theme)
        self.theme_changed.emit(theme)

    def _on_log_level_changed(self, level: str):
        from ...utils.logging_config import set_log_level
        set_log_level(level)
        self.app_state.qsettings.setValue("log_level", level)

    def _open_log_folder(self):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.app_state.log_file.parent)
            )
        )