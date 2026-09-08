from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QButtonGroup
)
from PySide6.QtGui import QGuiApplication

from .theme import build_stylesheet
from .pages.dashboard_page import DashboardPage
from .pages.catalogue_page import CataloguePage
from .pages.profiles_page import ProfilesPage
from .pages.jobs_page import JobsPage
from .pages.snapshots_page import SnapshotsPage
from .pages.settings_page import SettingsPage

NAV_ITEMS = [
    ("dashboard", "🏠", "Dashboard"),
    ("catalogue", "🧰", "Tool Catalogue"),
    ("profiles", "📦", "Profiles"),
    ("jobs", "⚙", "Jobs"),
    ("snapshots", "🗂", "Snapshots"),
    ("settings", "⚙️", "Settings"),
]

PAGE_TITLES = {
    "dashboard": ("Dashboard", "Overview of your forensic workstation environment"),
    "catalogue": ("Tool Catalogue", "Browse and install forensic tools"),
    "profiles": ("Profiles", "Curated environment bundles"),
    "jobs": ("Jobs & Installations", "Track installation progress and history"),
    "snapshots": ("Snapshots", "Save and restore environment states"),
    "settings": ("Settings", "Configure directories, theme, and logging"),
}


class MainWindow(QMainWindow):
    def __init__(self, app, app_state):
        super().__init__()
        self.app = app
        self.app_state = app_state

        self.setWindowTitle("Forensic Workstation Builder")
        self.resize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---------------- Sidebar ----------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        brand = QLabel("🛡  FWB")
        brand.setObjectName("SidebarBrand")
        sidebar_layout.addWidget(brand)
        subtitle = QLabel("Forensic Workstation Builder")
        subtitle.setObjectName("SidebarSubtitle")
        subtitle.setWordWrap(True)
        sidebar_layout.addWidget(subtitle)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = {}
        for key, icon, label in NAV_ITEMS:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.navigate(k))
            sidebar_layout.addWidget(btn)
            self.nav_group.addButton(btn)
            self.nav_buttons[key] = btn

        sidebar_layout.addStretch()
        version_label = QLabel("v0.1.0")
        version_label.setObjectName("SidebarSubtitle")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)
        outer.addWidget(sidebar)

        # ---------------- Right side (header + content) ----------------
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 0, 28, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        self.header_title = QLabel()
        self.header_title.setObjectName("HeaderTitle")
        self.header_subtitle = QLabel()
        self.header_subtitle.setObjectName("HeaderSubtitle")
        title_col.addWidget(self.header_title)
        title_col.addWidget(self.header_subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        self.status_pill = QLabel("● Backend Ready")
        self.status_pill.setObjectName("StatusPill")
        header_layout.addWidget(self.status_pill)
        right.addWidget(header)

        content_area = QWidget()
        content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.pages = {
            "dashboard": DashboardPage(self.app_state),
            "catalogue": CataloguePage(self.app_state),
            "profiles": ProfilesPage(self.app_state),
            "jobs": JobsPage(self.app_state),
            "snapshots": SnapshotsPage(self.app_state),
            "settings": SettingsPage(self.app_state),
        }
        for key, _, _ in NAV_ITEMS:
            self.stack.addWidget(self.pages[key])
        content_layout.addWidget(self.stack)
        right.addWidget(content_area, 1)

        right_widget = QWidget()
        right_widget.setLayout(right)
        outer.addWidget(right_widget, 1)

        # Wire cross-page refresh
        self.app_state.data_changed.connect(self._refresh_all)
        self.pages["settings"].theme_changed.connect(self.apply_theme)

        self.navigate("dashboard")

    def navigate(self, key: str):
        self.nav_buttons[key].setChecked(True)
        self.stack.setCurrentWidget(self.pages[key])
        title, subtitle = PAGE_TITLES[key]
        self.header_title.setText(title)
        self.header_subtitle.setText(subtitle)
        refresh = getattr(self.pages[key], "refresh", None)
        if callable(refresh):
            refresh()

    def _refresh_all(self):
        for page in self.pages.values():
            refresh = getattr(page, "refresh", None)
            if callable(refresh):
                refresh()

    def apply_theme(self, theme_name: str):
        self.app.setStyleSheet(build_stylesheet(theme_name))
