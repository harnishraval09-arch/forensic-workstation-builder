from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QScrollArea, QGridLayout, QPushButton
)

from ..components.tool_card import ToolCard
from ..components.tool_detail_dialog import ToolDetailDialog
from ..components.progress_dialog import ProgressDialog
from ..workers import InstallWorker

COLUMNS = 3


class CataloguePage(QWidget):
    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state
        self._workers = {}  # tool_id -> InstallWorker (kept alive)
        self._progress_dialogs = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Tool Catalogue")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        # Search + filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tools by name or description…")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self.search_input, 2)

        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.category_filter, 1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All statuses", "Installed", "Not installed"])
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filter_row.addWidget(self.status_filter, 1)
        root.addLayout(filter_row)

        self.result_count_label = QLabel()
        self.result_count_label.setObjectName("Muted")
        root.addWidget(self.result_count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_container = QWidget()
        self.grid = QGridLayout(grid_container)
        self.grid.setSpacing(16)
        self.grid.setContentsMargins(0, 0, 0, 4)
        scroll.setWidget(grid_container)
        root.addWidget(scroll, 1)

        self._cards = []
        self.refresh()

    # -------------------------------------------------------------- #
    def refresh(self):
        tools = self.app_state.tool_manager.list_tools()
        categories = ["All categories"] + sorted({t.category for t in tools})
        current = self.category_filter.currentText()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItems(categories)
        if current in categories:
            self.category_filter.setCurrentText(current)
        self.category_filter.blockSignals(False)

        self._rebuild_cards(tools)

    def _rebuild_cards(self, tools):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cards = []

        for tool in sorted(tools, key=lambda t: t.name.lower()):
            card = ToolCard(tool)
            card.clicked.connect(self._open_details)
            card.install_requested.connect(self._install_tool)
            self._cards.append(card)

        self._apply_filters()

    def _apply_filters(self):
        query = self.search_input.text().strip().lower()
        category = self.category_filter.currentText()
        status = self.status_filter.currentText()

        while self.grid.count():
            self.grid.takeAt(0)

        visible = []
        for card in self._cards:
            tool = card.tool
            matches_query = (
                not query
                or query in tool.name.lower()
                or query in tool.description.lower()
            )
            matches_category = category in ("", "All categories") or tool.category == category
            matches_status = (
                status == "All statuses"
                or (status == "Installed" and tool.installed)
                or (status == "Not installed" and not tool.installed)
            )
            card.setVisible(matches_query and matches_category and matches_status)
            if matches_query and matches_category and matches_status:
                visible.append(card)

        for index, card in enumerate(visible):
            row, col = divmod(index, COLUMNS)
            self.grid.addWidget(card, row, col)

        self.result_count_label.setText(f"{len(visible)} tool(s)")

    # -------------------------------------------------------------- #
    def _open_details(self, tool_id: str):
        tool = self.app_state.tool_manager.get_tool(tool_id)
        if not tool:
            return
        dialog = ToolDetailDialog(tool, self.app_state.tool_manager, self)
        dialog.install_requested.connect(lambda tid: (dialog.close(), self._install_tool(tid)))
        dialog.uninstall_requested.connect(lambda tid: (dialog.close(), self._uninstall_tool(tid)))
        dialog.exec()

    def _install_tool(self, tool_id: str):
        tool = self.app_state.tool_manager.get_tool(tool_id)
        if not tool:
            return
        if tool_id in self._workers:
            return  # already installing

        job = self.app_state.job_store.start_job(tool_id, tool.name)
        self.app_state.activity_log.add(f"Started installing {tool.name}", "info")

        progress = ProgressDialog(f"Installing {tool.name}", self)
        progress.set_status(f"Resolving and installing {tool.name}…")
        self._progress_dialogs[tool_id] = progress

        worker = InstallWorker(self.app_state.tool_manager, tool_id)
        self._workers[tool_id] = worker

        def on_finished(tid, success, message):
            self.app_state.job_store.complete_job(job.job_id, success, message)
            level = "success" if success else "error"
            self.app_state.activity_log.add(f"{tool.name}: {message}", level)
            progress.mark_complete(success, message)
            self._workers.pop(tid, None)
            self.refresh()
            self.app_state.on_data_changed()

        worker.finished_job.connect(on_finished)
        worker.start()
        progress.exec()

    def _uninstall_tool(self, tool_id: str):
        installer = self.app_state.installer
        tool = self.app_state.tool_manager.get_tool(tool_id)
        if not tool:
            return
        success, message = installer.uninstall_tool(tool)
        if success:
            tool.installed = False
            self.app_state.tool_manager.installed_tools.pop(tool_id, None)
        self.app_state.activity_log.add(f"{tool.name}: {message}", "success" if success else "error")
        self.refresh()
        self.app_state.on_data_changed()
