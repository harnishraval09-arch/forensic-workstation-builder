"""
Audit Log page.

Originally written against a standalone data/logs/audit.log JSON-lines
file, but nothing in this app writes to that file - it would just be
an empty table forever. Every notable action (install, uninstall,
profile install, snapshot created/deleted, settings changed) already
gets recorded via AppState.activity_log.add(...) across the other
pages, so this page reads from there instead of adding a second,
unsynced logging path. If a durable trail that survives an app
restart is needed later, this is the one place to add a file-backed
writer - everything else keeps working unchanged.
"""

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QAbstractItemView, QFileDialog, QMessageBox
)

from ..components.stat_card import StatCard

LEVEL_COLORS = {
    "info": "#2f6fed",
    "success": "#27ae60",
    "warning": "#e67e22",
    "error": "#e74c3c",
}


class AuditPage(QWidget):
    """Searchable, filterable view over the in-session activity trail."""

    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        title = QLabel("Audit Log")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        root.addWidget(title)

        sub = QLabel("Full trail of installs, uninstalls, and configuration changes this session.")
        sub.setObjectName("Muted")
        root.addWidget(sub)

        # --- Filter row ---------------------------------------------------
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events…")
        self.search_input.textChanged.connect(self.refresh)
        filter_row.addWidget(self.search_input, 2)

        self.level_filter = QComboBox()
        self.level_filter.addItems(["All levels", "Success", "Info", "Warning", "Error"])
        self.level_filter.currentIndexChanged.connect(self.refresh)
        filter_row.addWidget(self.level_filter, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        filter_row.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.setObjectName("GhostButton")
        clear_btn.clicked.connect(self._clear_filters)
        filter_row.addWidget(clear_btn)
        root.addLayout(filter_row)

        # --- Stat cards ------------------------------------------------
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_total = StatCard("Total Events", 0, "📋", "#2f6fed")
        self.stat_success = StatCard("Success", 0, "✅", "#27ae60")
        self.stat_warning = StatCard("Warnings", 0, "⚠", "#e67e22")
        self.stat_error = StatCard("Errors", 0, "⛔", "#e74c3c")
        for card in (self.stat_total, self.stat_success, self.stat_warning, self.stat_error):
            stats_row.addWidget(card)
        root.addLayout(stats_row)

        # --- Table -------------------------------------------------------
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Time", "Event", "Level"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        root.addWidget(self.table, 1)

        export_btn = QPushButton("Export Audit Log")
        export_btn.setObjectName("PrimaryButton")
        export_btn.clicked.connect(self._export)
        export_row = QHBoxLayout()
        export_row.addWidget(export_btn)
        export_row.addStretch()
        root.addLayout(export_row)

        self.app_state.activity_log.changed.connect(self.refresh)
        self.refresh()

    # -------------------------------------------------------------- #
    def _filtered_events(self):
        events = self.app_state.activity_log.recent(500)
        level_filter = self.level_filter.currentText()
        search = self.search_input.text().strip().lower()

        filtered = []
        for e in events:
            if level_filter != "All levels" and e.level != level_filter.lower():
                continue
            if search and search not in e.message.lower():
                continue
            filtered.append(e)
        return filtered

    def refresh(self):
        filtered = self._filtered_events()

        self.stat_total.set_value(len(filtered))
        self.stat_success.set_value(sum(1 for e in filtered if e.level == "success"))
        self.stat_warning.set_value(sum(1 for e in filtered if e.level == "warning"))
        self.stat_error.set_value(sum(1 for e in filtered if e.level == "error"))

        self.table.setRowCount(len(filtered))
        for row, e in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(e.timestamp))
            self.table.setItem(row, 1, QTableWidgetItem(e.message))
            level_item = QTableWidgetItem(e.level.upper())
            level_item.setForeground(QColor(LEVEL_COLORS.get(e.level, "#8a97a3")))
            self.table.setItem(row, 2, level_item)

    def _clear_filters(self):
        self.level_filter.setCurrentIndex(0)
        self.search_input.clear()

    def _export(self):
        events = self._filtered_events()
        if not events:
            QMessageBox.information(self, "Nothing to export", "There are no audit events matching the current filters.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Audit Log", "audit_export.json", "JSON Files (*.json)")
        if not path:
            return
        data = [{"timestamp": e.timestamp, "message": e.message, "level": e.level} for e in events]
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Export complete", f"Audit log exported to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))