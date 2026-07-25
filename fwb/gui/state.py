"""
GUI-side application state that the backend does not yet track:

- ActivityLog: rolling feed of user-visible events for the Dashboard
- JobRecord / JobStore: install job bookkeeping for the Jobs page
- SnapshotStore: simple JSON-based snapshot persistence for the
  Snapshots page (there is no SnapshotManager in the backend yet, so
  this reads/writes plain JSON files under data/snapshots/)

These are intentionally simple, dependency-free classes so the GUI
has something real to bind to instead of static placeholder data.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QObject, Signal


# ------------------------------------------------------------------ #
# Activity log
# ------------------------------------------------------------------ #
@dataclass
class ActivityEvent:
    timestamp: str
    message: str
    level: str = "info"  # info | success | warning | error


class ActivityLog(QObject):
    changed = Signal()

    def __init__(self, max_events: int = 50):
        super().__init__()
        self._events: List[ActivityEvent] = []
        self._max = max_events

    def add(self, message: str, level: str = "info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self._events.insert(0, ActivityEvent(timestamp=ts, message=message, level=level))
        self._events = self._events[: self._max]
        self.changed.emit()

    def recent(self, count: int = 8) -> List[ActivityEvent]:
        return self._events[:count]


# ------------------------------------------------------------------ #
# Jobs
# ------------------------------------------------------------------ #
@dataclass
class JobRecord:
    job_id: str
    tool_id: str
    tool_name: str
    status: str = "running"  # running | success | failed
    message: str = ""
    started_at: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    finished_at: Optional[str] = None


class JobStore(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._jobs: List[JobRecord] = []
        self._counter = 0

    def start_job(self, tool_id: str, tool_name: str) -> JobRecord:
        self._counter += 1
        job = JobRecord(job_id=f"job-{self._counter}", tool_id=tool_id, tool_name=tool_name)
        self._jobs.insert(0, job)
        self.changed.emit()
        return job

    def complete_job(self, job_id: str, success: bool, message: str):
        for job in self._jobs:
            if job.job_id == job_id:
                job.status = "success" if success else "failed"
                job.message = message
                job.finished_at = datetime.now().strftime("%H:%M:%S")
                break
        self.changed.emit()

    def running(self) -> List[JobRecord]:
        return [j for j in self._jobs if j.status == "running"]

    def completed(self) -> List[JobRecord]:
        return [j for j in self._jobs if j.status != "running"]

    def all(self) -> List[JobRecord]:
        return list(self._jobs)


# ------------------------------------------------------------------ #
# Snapshots (GUI-managed, JSON-file backed)
# ------------------------------------------------------------------ #
class SnapshotStore:
    """
    Lightweight snapshot persistence. A snapshot records the set of
    currently-installed tool IDs plus a label/timestamp so an
    environment can be reproduced later. This is implemented at the
    GUI layer since the backend does not yet expose a SnapshotManager.
    """

    def __init__(self, snapshots_dir: Path):
        self.snapshots_dir = snapshots_dir
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def create(self, name: str, tool_ids: List[str]) -> Path:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.snapshots_dir / f"{safe_name}_{ts}.json"
        data = {
            "name": name,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "tool_ids": tool_ids,
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return file_path

    def create_snapshot(self, name: str, description: str = "", tools: Optional[List] = None) -> Optional[Path]:
        """
        Create a snapshot from a list of Tool objects (e.g. from
        ToolManager.list_installed()). Stores both a flat "tool_ids"
        list (kept for backward compatibility with the Snapshots
        page's count display) and a richer "tools" list with
        per-tool version/path/pin metadata.
        """
        tools = tools or []
        try:
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower()) or "snapshot"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.snapshots_dir / f"{safe_name}_{ts}.json"
            data = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "tool_ids": [t.id for t in tools],
                "tools": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "version": t.version,
                        "install_path": t.install_path,
                        "pinned_version": getattr(t, "pinned_version", None),
                        "pinned_hash": getattr(t, "pinned_hash", None),
                    }
                    for t in tools
                ],
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return file_path
        except Exception:
            return None

    def list_snapshots(self) -> List[dict]:
        results = []
        for path in sorted(self.snapshots_dir.glob("*.json"), reverse=True):
            try:
                with open(path) as f:
                    data = json.load(f)
                data["_path"] = str(path)
                results.append(data)
            except Exception:
                continue
        return results

    def delete(self, path: str):
        p = Path(path)
        if p.exists() and p.is_relative_to(self.snapshots_dir):
            p.unlink()

    def export_to(self, source_path: str, dest_path: str):
        with open(source_path) as f:
            data = f.read()
        with open(dest_path, "w") as f:
            f.write(data)

    def import_from(self, source_path: str) -> Path:
        with open(source_path) as f:
            data = json.load(f)
        name = data.get("name", "imported")
        return self.create(name, data.get("tool_ids", []))