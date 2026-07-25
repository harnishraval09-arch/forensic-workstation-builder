from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QWidget
)


class InstallationPlanDialog(QDialog):
    """
    Shows the output of DependencyResolver.get_install_plan(): the
    tools that will be installed, grouped into dependency-ordered
    batches, plus whether admin rights will be required. The caller
    should proceed with installation only if exec() == QDialog.Accepted.
    """

    def __init__(self, plan: dict, tools_by_id: dict, title="Installation Plan", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(480, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 16)
        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        header_layout.addWidget(title_label)

        total = plan.get("total_tools", 0)
        admin = plan.get("needs_admin", False)
        summary_bits = [f"{total} tool(s) will be installed"]
        if admin:
            summary_bits.append("administrator privileges required")
        summary = QLabel(" · ".join(summary_bits))
        summary.setObjectName("Muted")
        header_layout.addWidget(summary)
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(14)

        batches = plan.get("batches", [])
        if not batches:
            empty = QLabel("Nothing to install — all selected tools are already installed.")
            empty.setObjectName("Muted")
            content_layout.addWidget(empty)
        else:
            for i, batch in enumerate(batches, start=1):
                batch_label = QLabel(f"Step {i}" + ("  (parallel-safe)" if len(batch) > 1 else ""))
                batch_label.setObjectName("CardTitle")
                content_layout.addWidget(batch_label)
                for tool_id in batch:
                    tool = tools_by_id.get(tool_id)
                    name = tool.name if tool else tool_id
                    version = tool.version if tool else ""
                    admin_flag = " · requires admin" if (tool and tool.requires_admin) else ""
                    row = QLabel(f"   • {name}  v{version}{admin_flag}")
                    content_layout.addWidget(row)

        content_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(24, 14, 24, 20)
        footer.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)
        confirm_btn = QPushButton("Confirm & Install")
        confirm_btn.setObjectName("PrimaryButton")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setEnabled(total > 0)
        footer.addWidget(confirm_btn)
        root.addLayout(footer)
