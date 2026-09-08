from pathlib import Path
from PySide6.QtCore import QObject, Signal, QSettings

from .state import ActivityLog, JobStore, SnapshotStore


class AppState(QObject):
    """Central hand-off point between the backend managers and the
    GUI. Holds references to ToolManager / ProfileManager /
    DependencyResolver / Installer plus GUI-only bookkeeping
    (activity log, job store, snapshots, persisted settings)."""

    data_changed = Signal()

    def __init__(self, tool_manager, profile_manager, dependency_resolver, installer,
                 data_dir: Path):
        super().__init__()
        self.tool_manager = tool_manager
        self.profile_manager = profile_manager
        self.dependency_resolver = dependency_resolver
        self.installer = installer

        self.data_dir = data_dir
        self.activity_log = ActivityLog()
        self.job_store = JobStore()
        self.snapshot_store = SnapshotStore(data_dir / "snapshots")
        self.log_file = data_dir / "logs" / "app.log"

        self.qsettings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")

    def on_data_changed(self):
        self.data_changed.emit()
