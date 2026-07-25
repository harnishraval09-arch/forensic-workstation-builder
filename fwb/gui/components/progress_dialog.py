from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
)


class ProgressDialog(QDialog):
    """
    Modal progress dialog used while an install job (or batch of jobs)
    is running. ToolManager does not report granular percentages, so
    the bar runs in indeterminate ("busy") mode; the status label is
    updated as each step completes. The Cancel button lets the user
    dismiss the dialog and let the job continue in the background
    (visible on the Jobs page) since the underlying subprocess calls
    cannot be safely interrupted mid-flight.
    """

    cancelled = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")
        layout.addWidget(self.title_label)

        self.status_label = QLabel("Starting…")
        self.status_label.setObjectName("Muted")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.cancel_btn = QPushButton("Run in background")
        self.cancel_btn.setObjectName("GhostButton")
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

    def set_status(self, text: str):
        self.status_label.setText(text)

    def mark_complete(self, success: bool, message: str):
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        icon = "✅" if success else "❌"
        self.status_label.setText(f"{icon} {message}")
        self.cancel_btn.setText("Close")

    def _on_cancel(self):
        self.cancelled.emit()
        self.close()
