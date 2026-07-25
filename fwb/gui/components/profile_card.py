from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from ..effects import apply_card_shadow


PROFILE_ICONS = {
    "Digital Forensics": "🖥",
    "Malware Analysis": "🧬",
    "Network Forensics": "🌐",
    "General": "🧰",
}


class ProfileCard(QFrame):
    install_requested = Signal(str)  # profile_id

    def __init__(
        self,
        profile,
        tool_count: int,
        installed_count: int,
        parent=None
    ):
        super().__init__(parent)

        self.profile = profile
        self.setObjectName("Card")
        self.setMinimumHeight(200)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(10)

        top_row = QHBoxLayout()

        icon = QLabel(PROFILE_ICONS.get(profile.category, "🧰"))
        icon.setFixedSize(42, 42)
        icon.setAlignment(Qt.AlignCenter)
        icon.setObjectName("IconBadge")

        icon.setStyleSheet(
            "background-color: qlineargradient("
            "x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #2f6fed33, stop:1 #2ec4b61a);"
            "border-radius: 12px;"
        )

        top_row.addWidget(icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)

        name = QLabel(profile.name)
        name.setObjectName("CardTitle")

        meta = QLabel(f"{profile.category} · v{profile.version}")
        meta.setObjectName("CardMeta")

        title_col.addWidget(name)
        title_col.addWidget(meta)

        top_row.addLayout(title_col)
        top_row.addStretch()

        root.addLayout(top_row)

        desc = QLabel(profile.description)
        desc.setObjectName("CardDesc")
        desc.setWordWrap(True)

        root.addWidget(desc)
        root.addStretch()

        progress_label = QLabel(
            f"{installed_count} / {tool_count} tools installed"
        )
        progress_label.setObjectName("Muted")
        root.addWidget(progress_label)

        btn_row = QHBoxLayout()

        install_btn = QPushButton(
            "Install Profile"
            if installed_count < tool_count
            else "Reinstall Profile"
        )

        install_btn.setObjectName("PrimaryButton")
        install_btn.clicked.connect(
            lambda: self.install_requested.emit(self.profile.id)
        )

        btn_row.addWidget(install_btn)
        btn_row.addStretch()

        root.addLayout(btn_row)

        apply_card_shadow(self)