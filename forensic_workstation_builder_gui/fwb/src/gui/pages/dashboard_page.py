from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout
)

from ..components.stat_card import StatCard


class DashboardPage(QWidget):
    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(22)

        # Welcome
        greeting = self._greeting()
        welcome = QLabel(f"{greeting} 👋")
        welcome.setStyleSheet("font-size: 22px; font-weight: 700;")
        root.addWidget(welcome)
        sub = QLabel("Here's the current state of your forensic workstation environment.")
        sub.setObjectName("Muted")
        root.addWidget(sub)

        # Stat cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.stat_available = StatCard("Available Tools", 0, "🧰", "#2f6fed")
        self.stat_installed = StatCard("Installed Tools", 0, "✅", "#27ae60")
        self.stat_updates = StatCard("Updates Available", 0, "⬆", "#e67e22")
        self.stat_profiles = StatCard("Profiles", 0, "📦", "#2ec4b6")
        for card in (self.stat_available, self.stat_installed, self.stat_updates, self.stat_profiles):
            stats_row.addWidget(card)
        root.addLayout(stats_row)

        # Middle: activity + status
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        activity_card = QFrame()
        activity_card.setObjectName("Card")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(18, 16, 18, 16)
        activity_title = QLabel("Recent Activity")
        activity_title.setObjectName("SectionTitle")
        activity_layout.addWidget(activity_title)
        self.activity_container = QVBoxLayout()
        self.activity_container.setSpacing(8)
        activity_layout.addLayout(self.activity_container)
        activity_layout.addStretch()
        mid_row.addWidget(activity_card, 2)

        status_card = QFrame()
        status_card.setObjectName("Card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(18, 16, 18, 16)
        status_title = QLabel("System Status")
        status_title.setObjectName("SectionTitle")
        status_layout.addWidget(status_title)
        self.status_container = QVBoxLayout()
        self.status_container.setSpacing(10)
        status_layout.addLayout(self.status_container)
        status_layout.addStretch()
        mid_row.addWidget(status_card, 1)

        root.addLayout(mid_row)
        root.addStretch()

        self.app_state.activity_log.changed.connect(self.refresh_activity)
        self.refresh()

    def _greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        if hour < 18:
            return "Good afternoon"
        return "Good evening"

    def refresh(self):
        tm = self.app_state.tool_manager
        pm = self.app_state.profile_manager
        tools = tm.list_tools()
        installed = tm.list_installed()
        updates = [t for t in installed if t.installed_version and t.installed_version != t.version]

        self.stat_available.set_value(len(tools))
        self.stat_installed.set_value(len(installed))
        self.stat_updates.set_value(len(updates))
        self.stat_profiles.set_value(len(pm.list_profiles()))

        self.refresh_activity()
        self._refresh_status()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def refresh_activity(self):
        self._clear_layout(self.activity_container)
        events = self.app_state.activity_log.recent(8)
        if not events:
            empty = QLabel("No activity yet. Install a tool to get started.")
            empty.setObjectName("Muted")
            self.activity_container.addWidget(empty)
            return
        colors = {"info": "#2f6fed", "success": "#27ae60", "warning": "#e67e22", "error": "#e74c3c"}
        for event in events:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {colors.get(event.level, '#3498db')}; font-size: 10px;")
            dot.setFixedWidth(16)
            row.addWidget(dot, 0, Qt.AlignTop)
            text = QLabel(f"{event.message}")
            text.setWordWrap(True)
            time_label = QLabel(event.timestamp)
            time_label.setObjectName("Muted")
            time_label.setFixedWidth(60)
            row.addWidget(text, 1)
            row.addWidget(time_label, 0, Qt.AlignTop)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.activity_container.addWidget(wrapper)

    def _refresh_status(self):
        self._clear_layout(self.status_container)
        tm = self.app_state.tool_manager
        rows = [
            ("Tools directory", str(tm.tools_dir)),
            ("Download directory", str(tm.tools_dir / "downloads")),
            ("Install directory", str(tm.tools_dir / "installed")),
            ("Loaded manifests", str(len(tm.tools))),
        ]
        for label_text, value_text in rows:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setObjectName("Muted")
            value = QLabel(value_text)
            value.setWordWrap(True)
            value.setAlignment(Qt.AlignRight)
            row.addWidget(label)
            row.addWidget(value, 1)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.status_container.addWidget(wrapper)
