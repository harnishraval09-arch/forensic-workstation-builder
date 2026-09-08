from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QComboBox, QFrame, QMessageBox
)


class CreateProfileDialog(QDialog):
    """Advanced dialog for authoring a new Profile from the currently
    loaded tool catalogue. Produces a Profile instance via get_profile()
    once accepted."""

    def __init__(self, all_tools, existing_ids, parent=None):
        super().__init__(parent)
        self.all_tools = all_tools
        self.existing_ids = existing_ids
        self.setWindowTitle("Create Profile")
        self.setMinimumSize(460, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 16)
        title = QLabel("Create Profile")
        title.setObjectName("HeaderTitle")
        header_layout.addWidget(title)
        subtitle = QLabel("Bundle tools into a reusable forensic environment profile.")
        subtitle.setObjectName("HeaderSubtitle")
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(24, 16, 24, 16)
        body.setSpacing(10)

        body.addWidget(QLabel("Profile ID"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. incident_response")
        body.addWidget(self.id_input)

        body.addWidget(QLabel("Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Incident Response")
        body.addWidget(self.name_input)

        body.addWidget(QLabel("Category"))
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        categories = sorted({t.category for t in all_tools}) or ["General"]
        self.category_input.addItems(categories)
        body.addWidget(self.category_input)

        body.addWidget(QLabel("Description"))
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(64)
        body.addWidget(self.description_input)

        body.addWidget(QLabel("Tools to include"))
        self.tools_list = QListWidget()
        self.tools_list.setSelectionMode(QListWidget.NoSelection)
        for tool in sorted(all_tools, key=lambda t: t.name.lower()):
            item = QListWidgetItem(f"{tool.name}  ({tool.category})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, tool.id)
            self.tools_list.addItem(item)
        body.addWidget(self.tools_list, 1)

        root.addLayout(body)

        footer = QHBoxLayout()
        footer.setContentsMargins(24, 8, 24, 20)
        footer.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)
        create_btn = QPushButton("Create Profile")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._on_create)
        footer.addWidget(create_btn)
        root.addLayout(footer)

    def _on_create(self):
        profile_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        if not profile_id or not name:
            QMessageBox.warning(self, "Missing information", "Profile ID and Name are required.")
            return
        if profile_id in self.existing_ids:
            QMessageBox.warning(self, "Duplicate ID", f"A profile with ID '{profile_id}' already exists.")
            return

        selected_ids = []
        for i in range(self.tools_list.count()):
            item = self.tools_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_ids.append(item.data(Qt.UserRole))

        if not selected_ids:
            QMessageBox.warning(self, "No tools selected", "Select at least one tool for this profile.")
            return

        self.result_data = {
            "id": profile_id,
            "name": name,
            "description": self.description_input.toPlainText().strip(),
            "category": self.category_input.currentText().strip() or "General",
            "tools": selected_ids,
        }
        self.accept()
