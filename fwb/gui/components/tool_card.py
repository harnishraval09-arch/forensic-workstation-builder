from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)

from ..effects import apply_card_shadow


CATEGORY_COLORS = {
    "Digital Forensics": "#2f6fed",
    "Malware Analysis": "#e74c3c",
    "Network Forensics": "#2ec4b6",
    "General": "#8a97a3",
}


# Distinctive glyph per known tool - a nod to each tool's own mascot/
# theme (Wireshark's shark fin, Ghidra's dragon, KAPE's kangaroo, Zeek's
# owl, etc.) rather than reproducing any actual trademarked logo.
TOOL_ICONS = {
    "cyberchef": "🍴",
    "wireshark": "🦈",
    "autopsy": "🔬",
    "registry_explorer": "🗄️",
    "evtxecmd": "📜",
    "volatility3": "🧪",
    "python3": "🐍",
    "ida_free": "🧠",
    "ghidra": "🐉",
    "pestudio": "🐜",
    "networkminer": "📡",
    "zeek": "🦉",
    "ftk_imager": "💽",
    "kape": "🦘",
}


def _icon_for(tool) -> str:
    if tool.id in TOOL_ICONS:
        return TOOL_ICONS[tool.id]

    words = [w for w in tool.name.replace("-", " ").split() if w]

    if not words:
        return "🧰"

    if len(words) == 1:
        return words[0][:2].upper()

    return (words[0][0] + words[1][0]).upper()


class ToolCard(QFrame):
    """Card for a single tool in the catalogue grid. Shows a status
    badge, install button, and emits signals for click/install."""

    clicked = Signal(str)              # tool_id
    install_requested = Signal(str)    # tool_id

    def __init__(self, tool, parent=None):
        super().__init__(parent)

        self.tool = tool
        self.setObjectName("Card")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        accent = CATEGORY_COLORS.get(tool.category, "#3498db")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        top_row = QHBoxLayout()

        icon = QLabel(_icon_for(tool))
        icon.setObjectName("IconBadge")
        icon.setFixedSize(42, 42)
        icon.setAlignment(Qt.AlignCenter)

        icon.setStyleSheet(
            f"background-color: qlineargradient("
            f"x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {accent}33, stop:1 {accent}1a);"
            f"color: {accent};"
            "border-radius: 11px; "
            "font-weight: 700;"
        )

        top_row.addWidget(icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)

        name_label = QLabel(tool.name)
        name_label.setObjectName("CardTitle")

        meta_label = QLabel(f"{tool.category} · v{tool.version}")
        meta_label.setObjectName("CardMeta")

        title_col.addWidget(name_label)
        title_col.addWidget(meta_label)

        top_row.addLayout(title_col)
        top_row.addStretch()

        root.addLayout(top_row)

        desc = QLabel(tool.description)
        desc.setObjectName("CardDesc")
        desc.setWordWrap(True)
        desc.setMaximumHeight(48)

        root.addWidget(desc)

        root.addStretch()

        badge_row = QHBoxLayout()

        self.badge = QLabel()
        badge_row.addWidget(self.badge)

        if tool.requires_admin:
            admin_badge = QLabel("ADMIN")
            admin_badge.setObjectName("BadgeAdmin")
            badge_row.addWidget(admin_badge)

        badge_row.addStretch()
        root.addLayout(badge_row)

        bottom_row = QHBoxLayout()

        self.install_btn = QPushButton()
        self.install_btn.setObjectName("PrimaryButton")
        self.install_btn.clicked.connect(self._on_install_clicked)

        bottom_row.addWidget(self.install_btn)
        bottom_row.addStretch()

        details_btn = QPushButton("Details")
        details_btn.setObjectName("GhostButton")
        details_btn.clicked.connect(
            lambda: self.clicked.emit(self.tool.id)
        )

        bottom_row.addWidget(details_btn)
        root.addLayout(bottom_row)

        apply_card_shadow(self)

        self.refresh()

    def refresh(self):
        if self.tool.installed:
            self.badge.setText("INSTALLED")
            self.badge.setObjectName("BadgeInstalled")
            self.install_btn.setText("Reinstall")
            self.install_btn.setEnabled(True)
        else:
            self.badge.setText("NOT INSTALLED")
            self.badge.setObjectName("BadgeNotInstalled")
            self.install_btn.setText("Install")
            self.install_btn.setEnabled(True)

        # Force stylesheet re-evaluation for the badge's dynamic objectName
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)

    def _on_install_clicked(self):
        self.install_requested.emit(self.tool.id)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool.id)

        super().mousePressEvent(event)