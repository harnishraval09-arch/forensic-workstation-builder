from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QInputDialog, QFileDialog, QMessageBox
)


class SnapshotsPage(QWidget):
    """
    Snapshots capture the current set of installed tool IDs so an
    environment can be reproduced later. There is no SnapshotManager
    in the backend yet, so this page persists snapshots as plain JSON
    files via SnapshotStore (see gui/state.py).
    """

    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self.app_state = app_state

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Snapshots")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        create_btn = QPushButton("+ Create Snapshot")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self._create_snapshot)
        header.addWidget(create_btn)
        root.addLayout(header)

        sub = QLabel("Save the current set of installed tools as a reusable environment snapshot.")
        sub.setObjectName("Muted")
        root.addWidget(sub)

        actions_row = QHBoxLayout()
        export_btn = QPushButton("Export…")
        export_btn.clicked.connect(self._export_snapshot)
        import_btn = QPushButton("Import…")
        import_btn.clicked.connect(self._import_snapshot)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self._delete_snapshot)
        actions_row.addWidget(export_btn)
        actions_row.addWidget(import_btn)
        actions_row.addWidget(delete_btn)
        actions_row.addStretch()
        root.addLayout(actions_row)

        self.list_widget = QListWidget()
        root.addWidget(self.list_widget, 1)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        snapshots = self.app_state.snapshot_store.list_snapshots()
        if not snapshots:
            item = QListWidgetItem("No snapshots yet. Create one to save your current environment.")
            item.setFlags(item.flags() & ~item.flags())  # non-interactive placeholder
            self.list_widget.addItem(item)
            return
        for snap in snapshots:
            count = len(snap.get("tool_ids", []))
            label = f"{snap.get('name', 'Unnamed')}  ·  {count} tool(s)  ·  {snap.get('created_at', '')}"
            item = QListWidgetItem(label)
            item.setData(1000, snap.get("_path"))
            self.list_widget.addItem(item)

    def _create_snapshot(self):
        installed = self.app_state.tool_manager.list_installed()
        if not installed:
            QMessageBox.information(
                self, "Nothing installed",
                "No tools are currently installed, so there is nothing to snapshot yet."
            )
            return
        name, ok = QInputDialog.getText(self, "Create Snapshot", "Snapshot name:")
        if not ok or not name.strip():
            return
        tool_ids = [t.id for t in installed]
        self.app_state.snapshot_store.create(name.strip(), tool_ids)
        self.app_state.activity_log.add(f"Created snapshot '{name.strip()}' ({len(tool_ids)} tools)", "success")
        self.refresh()

    def _selected_path(self):
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(1000)

    def _export_snapshot(self):
        path = self._selected_path()
        if not path:
            QMessageBox.information(self, "Select a snapshot", "Select a snapshot to export first.")
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Export Snapshot", "snapshot.json", "JSON Files (*.json)")
        if dest:
            self.app_state.snapshot_store.export_to(path, dest)
            self.app_state.activity_log.add("Exported snapshot", "info")

    def _import_snapshot(self):
        src, _ = QFileDialog.getOpenFileName(self, "Import Snapshot", "", "JSON Files (*.json)")
        if src:
            self.app_state.snapshot_store.import_from(src)
            self.app_state.activity_log.add("Imported snapshot", "success")
            self.refresh()

    def _delete_snapshot(self):
        path = self._selected_path()
        if not path:
            QMessageBox.information(self, "Select a snapshot", "Select a snapshot to delete first.")
            return
        if QMessageBox.question(self, "Delete Snapshot", "Delete this snapshot?") == QMessageBox.Yes:
            self.app_state.snapshot_store.delete(path)
            self.app_state.activity_log.add("Deleted snapshot", "warning")
            self.refresh()
