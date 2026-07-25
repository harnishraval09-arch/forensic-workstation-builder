from pathlib import Path
from PySide6.QtCore import QObject, Signal, QSettings

from .state import ActivityLog, JobStore, SnapshotStore
from ..utils.logger import log_audit


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
        self.activity_log = ActivityLog(max_events=500)
        self.job_store = JobStore()
        self.snapshot_store = SnapshotStore(data_dir / "snapshots")
        self.log_file = data_dir / "logs" / "app.log"

        self.qsettings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")
        
        # Connect activity log changes to data_changed
        self.activity_log.changed.connect(self.on_data_changed)

    def on_data_changed(self):
        self.data_changed.emit()
    
    def add_activity(self, message: str, level: str = "info"):
        """Add activity with audit logging"""
        self.activity_log.add(message, level)
        log_audit("ui_activity", status=level, details={"message": message})
    
    def get_tools(self):
        """Get all available tools"""
        return list(self.tool_manager.tools.values())
    
    def get_installed_tools(self):
        """Get installed tools"""
        return list(self.tool_manager.installed_tools.values())
    
    def get_profiles(self):
        """Get all profiles"""
        return self.profile_manager.list_profiles()
    
    def install_tool(self, tool_id: str, progress_callback=None):
        """Install a tool via the backend with audit"""
        log_audit("install_requested", tool_id=tool_id, status="info")
        return self.tool_manager.install_tool(tool_id)
    
    def install_profile(self, profile_id: str):
        """Install all tools in a profile with audit"""
        profile = self.profile_manager.get_profile(profile_id)
        if not profile:
            log_audit("profile_install_failed", status="error", 
                      details={"profile_id": profile_id, "reason": "Not found"})
            return False, f"Profile '{profile_id}' not found"
        
        log_audit("profile_install_started", status="info", 
                  details={"profile_id": profile_id, "tool_count": len(profile.tools)})
        
        results = []
        for tool_id in profile.tools:
            success, msg = self.tool_manager.install_tool(tool_id)
            results.append((tool_id, success, msg))
            
            if not success:
                log_audit("profile_install_failed", status="error",
                          details={
                              "profile_id": profile_id,
                              "failed_tool": tool_id,
                              "reason": msg
                          })
                break
        
        all_success = all(r[1] for r in results)
        
        if all_success:
            log_audit("profile_install_completed", status="success",
                      details={
                          "profile_id": profile_id,
                          "tools_installed": len(results)
                      })
        
        return all_success, results
    
    def create_snapshot(self, name: str, description: str = ""):
        """Create snapshot with audit"""
        log_audit("snapshot_create_started", status="info", 
                  details={"snapshot_name": name})
        
        result = self.snapshot_store.create_snapshot(
            name=name,
            description=description,
            tools=self.get_installed_tools()
        )
        
        if result:
            log_audit("snapshot_create_completed", status="success",
                      details={"snapshot_name": name})
        else:
            log_audit("snapshot_create_failed", status="error",
                      details={"snapshot_name": name})
        
        return result