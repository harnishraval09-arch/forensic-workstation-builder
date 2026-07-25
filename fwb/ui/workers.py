"""
Background workers that call into ToolManager without blocking the UI
thread. ToolManager.install_tool() is synchronous and does not expose
granular progress, so these workers report coarse start/finish events;
the UI shows an indeterminate (busy) progress bar while a job runs.
"""

from PySide6.QtCore import QThread, Signal


class InstallWorker(QThread):
    """Installs a single tool (ToolManager.install_tool already walks
    that tool's dependency chain recursively)."""

    finished_job = Signal(str, bool, str)  # tool_id, success, message

    def __init__(self, tool_manager, tool_id: str, parent=None):
        super().__init__(parent)
        self.tool_manager = tool_manager
        self.tool_id = tool_id

    def run(self):
        try:
            success, message = self.tool_manager.install_tool(self.tool_id)
        except Exception as exc:  # defensive - keep the UI thread alive
            success, message = False, f"Unexpected error: {exc}"
        self.finished_job.emit(self.tool_id, success, message)


class BatchInstallWorker(QThread):
    """Installs an ordered list of tool IDs (e.g. a resolved profile
    installation plan), emitting a signal after each tool completes."""

    tool_finished = Signal(str, bool, str)   # tool_id, success, message
    batch_finished = Signal(int, int)        # succeeded, failed

    def __init__(self, tool_manager, tool_ids: list, parent=None):
        super().__init__(parent)
        self.tool_manager = tool_manager
        self.tool_ids = tool_ids

    def run(self):
        succeeded, failed = 0, 0
        for tool_id in self.tool_ids:
            tool = self.tool_manager.get_tool(tool_id)
            if tool and tool.installed:
                succeeded += 1
                self.tool_finished.emit(tool_id, True, "Already installed")
                continue
            try:
                success, message = self.tool_manager.install_tool(tool_id)
            except Exception as exc:
                success, message = False, f"Unexpected error: {exc}"
            if success:
                succeeded += 1
            else:
                failed += 1
            self.tool_finished.emit(tool_id, success, message)
        self.batch_finished.emit(succeeded, failed)
