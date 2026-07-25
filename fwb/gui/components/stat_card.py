from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

from ..effects import apply_card_shadow


class StatCard(QFrame):
    """Small dashboard statistic card: big number, label, and an
    accent-colored icon glyph."""

    def __init__(
        self,
        label: str,
        value,
        icon: str = "•",
        accent: str = "#3498db",
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setMinimumHeight(96)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(44, 44)
        icon_label.setAlignment(Qt.AlignCenter)

        icon_label.setStyleSheet(
            f"background-color: qlineargradient("
            f"x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {accent}33, stop:1 {accent}1a);"
            f"color: {accent};"
            "border-radius: 12px; "
            "font-size: 20px; "
            "font-weight: 700;"
        )

        outer.addWidget(icon_label)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("StatValue")

        self.label_label = QLabel(label.upper())
        self.label_label.setObjectName("StatLabel")

        text_col.addWidget(self.value_label)
        text_col.addWidget(self.label_label)

        outer.addLayout(text_col)
        outer.addStretch()

        apply_card_shadow(self)

    def set_value(self, value):
        self.value_label.setText(str(value))