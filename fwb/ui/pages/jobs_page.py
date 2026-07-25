from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)


class JobsPage(QWidget):
    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(18)

        title = QLabel("Jobs & Installations")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        root.addWidget(title)

        running_title = QLabel("Running")
        running_title.setObjectName("SectionTitle")
        root.addWidget(running_title)

        self.running_container = QVBoxLayout()
        self.running_container.setSpacing(10)
        running_wrapper = QWidget()
        running_wrapper.setLayout(self.running_container)
        root.addWidget(running_wrapper)

        completed_title = QLabel("Completed")
        completed_title.setObjectName("SectionTitle")
        root.addWidget(completed_title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Tool", "Status", "Started", "Finished", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        root.addWidget(self.table, 1)

        self.app_state.job_store.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        # Running jobs
        while self.running_container.count():
            item = self.running_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        running = self.app_state.job_store.running()
        if not running:
            empty = QLabel("No installations currently running.")
            empty.setObjectName("Muted")
            self.running_container.addWidget(empty)
        else:
            for job in running:
                card = QFrame()
                card.setObjectName("Card")
                layout = QVBoxLayout(card)
                layout.setContentsMargins(16, 12, 16, 12)
                top = QHBoxLayout()
                name = QLabel(job.tool_name)
                name.setObjectName("CardTitle")
                top.addWidget(name)
                top.addStretch()
                started = QLabel(f"Started {job.started_at}")
                started.setObjectName("Muted")
                top.addWidget(started)
                layout.addLayout(top)
                bar = QProgressBar()
                bar.setRange(0, 0)
                bar.setTextVisible(False)
                layout.addWidget(bar)
                self.running_container.addWidget(card)

        # Completed jobs
        completed = self.app_state.job_store.completed()
        self.table.setRowCount(len(completed))
        for row, job in enumerate(completed):
            status_item = QTableWidgetItem("Success" if job.status == "success" else "Failed")
            if job.status == "success":
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.table.setItem(row, 0, QTableWidgetItem(job.tool_name))
            self.table.setItem(row, 1, status_item)
            self.table.setItem(row, 2, QTableWidgetItem(job.started_at))
            self.table.setItem(row, 3, QTableWidgetItem(job.finished_at or ""))
            self.table.setItem(row, 4, QTableWidgetItem(job.message))
