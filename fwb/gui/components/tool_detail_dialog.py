from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)


def _row(label_text: str, value_text: str) -> QHBoxLayout:
    row = QHBoxLayout()
    label = QLabel(label_text)
    label.setObjectName("Muted")
    label.setFixedWidth(130)
    value = QLabel(value_text)
    value.setWordWrap(True)
    row.addWidget(label)
    row.addWidget(value, 1)
    return row


class ToolDetailDialog(QDialog):
    """Detail view for a single tool: metadata, dependencies, and
    install/uninstall actions wired to ToolManager."""

    install_requested = Signal(str)    # tool_id
    uninstall_requested = Signal(str)  # tool_id

    def __init__(self, tool, tool_manager, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.tool_manager = tool_manager
        self.setWindowTitle(tool.name)
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 18)
        header_layout.setSpacing(4)

        name_row = QHBoxLayout()
        name_label = QLabel(tool.name)
        name_label.setObjectName("HeaderTitle")
        name_row.addWidget(name_label)
        name_row.addStretch()
        self.status_badge = QLabel("INSTALLED" if tool.installed else "NOT INSTALLED")
        self.status_badge.setObjectName("BadgeInstalled" if tool.installed else "BadgeNotInstalled")
        name_row.addWidget(self.status_badge)
        header_layout.addLayout(name_row)

        subtitle = QLabel(f"{tool.category}  ·  v{tool.version}  ·  source: {tool.source}")
        subtitle.setObjectName("HeaderSubtitle")
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(24, 18, 24, 20)
        body.setSpacing(12)

        desc = QLabel(tool.description)
        desc.setWordWrap(True)
        body.addWidget(desc)

        body.addLayout(_row("Install method", tool.install_method))
        body.addLayout(_row("Supported OS", ", ".join(tool.supported_os)))
        body.addLayout(_row("Requires admin", "Yes" if tool.requires_admin else "No"))

        deps = tool.dependencies or []
        if deps:
            dep_names = []
            for dep_id in deps:
                dep_tool = self.tool_manager.get_tool(dep_id)
                dep_names.append(dep_tool.name if dep_tool else dep_id)
            body.addLayout(_row("Dependencies", ", ".join(dep_names)))
        else:
            body.addLayout(_row("Dependencies", "None"))

        if tool.install_path:
            body.addLayout(_row("Install path", tool.install_path))

        if tool.documentation_url:
            doc_link = QLabel(f'<a href="{tool.documentation_url}">{tool.documentation_url}</a>')
            doc_link.setOpenExternalLinks(True)
            doc_row = QHBoxLayout()
            lbl = QLabel("Documentation")
            lbl.setObjectName("Muted")
            lbl.setFixedWidth(130)
            doc_row.addWidget(lbl)
            doc_row.addWidget(doc_link, 1)
            body.addLayout(doc_row)

        body.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        if tool.installed:
            uninstall_btn = QPushButton("Uninstall")
            uninstall_btn.setObjectName("DangerButton")
            uninstall_btn.clicked.connect(lambda: self.uninstall_requested.emit(self.tool.id))
            btn_row.addWidget(uninstall_btn)
            reinstall_btn = QPushButton("Reinstall")
            reinstall_btn.setObjectName("PrimaryButton")
            reinstall_btn.clicked.connect(lambda: self.install_requested.emit(self.tool.id))
            btn_row.addWidget(reinstall_btn)
        else:
            install_btn = QPushButton("Install")
            install_btn.setObjectName("PrimaryButton")
            install_btn.clicked.connect(lambda: self.install_requested.emit(self.tool.id))
            btn_row.addWidget(install_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        body.addLayout(btn_row)

        root.addLayout(body)
