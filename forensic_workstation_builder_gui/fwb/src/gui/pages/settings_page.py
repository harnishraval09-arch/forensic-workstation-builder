import logging
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QFileDialog, QMessageBox
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)  # "dark" | "light"

    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        settings = app_state.qsettings

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(18)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        root.addWidget(title)

        # --- Directories -------------------------------------------------
        dirs_card = self._card("Directories")
        dirs_layout = dirs_card.layout()

        self.download_dir_input = QLineEdit(str(app_state.tool_manager.tools_dir / "downloads"))
        dirs_layout.addLayout(self._dir_row("Download directory", self.download_dir_input))

        self.install_dir_input = QLineEdit(str(app_state.tool_manager.tools_dir / "installed"))
        dirs_layout.addLayout(self._dir_row("Installation directory", self.install_dir_input))

        save_dirs_btn = QPushButton("Save Directories")
        save_dirs_btn.setObjectName("PrimaryButton")
        save_dirs_btn.clicked.connect(self._save_directories)
        dirs_layout.addWidget(save_dirs_btn)
        root.addWidget(dirs_card)

        # --- Appearance ----------------------------------------------------
        appearance_card = self._card("Appearance")
        appearance_layout = appearance_card.layout()
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = settings.value("theme", "dark")
        self.theme_combo.setCurrentText("Dark" if current_theme == "dark" else "Light")
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        appearance_layout.addLayout(theme_row)
        root.addWidget(appearance_card)

        # --- Updates ---------------------------------------------------
        updates_card = self._card("Update Policy")
        updates_layout = updates_card.layout()
        policy_row = QHBoxLayout()
        policy_row.addWidget(QLabel("When updates are available"))
        self.policy_combo = QComboBox()
        self.policy_combo.addItems(["Manual (ask before updating)", "Notify only", "Automatic"])
        self.policy_combo.setCurrentText(settings.value("update_policy", "Manual (ask before updating)"))
        self.policy_combo.currentTextChanged.connect(
            lambda v: settings.setValue("update_policy", v)
        )
        policy_row.addWidget(self.policy_combo)
        policy_row.addStretch()
        updates_layout.addLayout(policy_row)
        note = QLabel("Note: update detection isn't implemented in the backend yet — this only stores your preference.")
        note.setObjectName("Muted")
        note.setWordWrap(True)
        updates_layout.addWidget(note)
        root.addWidget(updates_card)

        # --- Logging -----------------------------------------------------
        logging_card = self._card("Logging")
        logging_layout = logging_card.layout()
        level_row = QHBoxLayout()
        level_row.addWidget(QLabel("Log level"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText(settings.value("log_level", "INFO"))
        self.log_level_combo.currentTextChanged.connect(self._on_log_level_changed)
        level_row.addWidget(self.log_level_combo)
        level_row.addStretch()
        logging_layout.addLayout(level_row)

        log_path_row = QHBoxLayout()
        log_path_label = QLabel(f"Log file: {self.app_state.log_file}")
        log_path_label.setObjectName("Muted")
        log_path_row.addWidget(log_path_label)
        log_path_row.addStretch()
        open_log_btn = QPushButton("Open Log Folder")
        open_log_btn.clicked.connect(self._open_log_folder)
        log_path_row.addWidget(open_log_btn)
        logging_layout.addLayout(log_path_row)
        root.addWidget(logging_card)

        root.addStretch()

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

    def _dir_row(self, label_text: str, line_edit: QLineEdit) -> QHBoxLayout:
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(170)
        row.addWidget(label)
        row.addWidget(line_edit, 1)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(lambda: self._browse(line_edit))
        row.addWidget(browse_btn)
        return row

    def _browse(self, line_edit: QLineEdit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if directory:
            line_edit.setText(directory)

    def _save_directories(self):
        settings = self.app_state.qsettings
        settings.setValue("download_dir", self.download_dir_input.text())
        settings.setValue("install_dir", self.install_dir_input.text())
        Path(self.download_dir_input.text()).mkdir(parents=True, exist_ok=True)
        Path(self.install_dir_input.text()).mkdir(parents=True, exist_ok=True)
        QMessageBox.information(
            self, "Saved",
            "Directory preferences saved. Restart the app to fully re-point ToolManager at new paths."
        )
        self.app_state.activity_log.add("Updated directory settings", "info")

    def _on_theme_changed(self, text: str):
        theme = "dark" if text == "Dark" else "light"
        self.app_state.qsettings.setValue("theme", theme)
        self.theme_changed.emit(theme)

    def _on_log_level_changed(self, level: str):
        self.app_state.qsettings.setValue("log_level", level)
        logging.getLogger().setLevel(getattr(logging, level, logging.INFO))
        self.app_state.activity_log.add(f"Log level set to {level}", "info")

    def _open_log_folder(self):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.app_state.log_file.parent)))
