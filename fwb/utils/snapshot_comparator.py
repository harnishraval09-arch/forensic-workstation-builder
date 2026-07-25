"""
Snapshot comparison utility - Compare two environment snapshots
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ToolDiff:
    """Represents a difference between two snapshots"""
    tool_id: str
    tool_name: str
    version_left: Optional[str]
    version_right: Optional[str]
    status: str  # "added", "removed", "version_changed", "same"


@dataclass
class SnapshotComparison:
    """Result of comparing two snapshots"""
    left_name: str
    right_name: str
    left_count: int
    right_count: int
    diffs: List[ToolDiff]
    
    @property
    def summary(self) -> str:
        added = sum(1 for d in self.diffs if d.status == "added")
        removed = sum(1 for d in self.diffs if d.status == "removed")
        changed = sum(1 for d in self.diffs if d.status == "version_changed")
        same = sum(1 for d in self.diffs if d.status == "same")
        
        return f"Added: {added}, Removed: {removed}, Version Changed: {changed}, Same: {same}"


class SnapshotComparator:
    """Compare two environment snapshots"""
    
    @staticmethod
    def load_snapshot(file_path: Path) -> Dict[str, Any]:
        """Load a snapshot from a JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def compare_snapshots(left: Dict[str, Any], right: Dict[str, Any]) -> SnapshotComparison:
        """
        Compare two snapshots and return the differences.
        
        Args:
            left: First snapshot data
            right: Second snapshot data
        
        Returns:
            SnapshotComparison object with all differences
        """
        left_tools = {t["id"]: t for t in left.get("tools", [])}
        right_tools = {t["id"]: t for t in right.get("tools", [])}
        
        all_ids = set(left_tools.keys()) | set(right_tools.keys())
        diffs = []
        
        for tool_id in sorted(all_ids):
            left_tool = left_tools.get(tool_id)
            right_tool = right_tools.get(tool_id)
            
            if not left_tool:
                # Tool only in right snapshot (added)
                diffs.append(ToolDiff(
                    tool_id=tool_id,
                    tool_name=right_tool.get("name", tool_id),
                    version_left=None,
                    version_right=right_tool.get("version", "unknown"),
                    status="added"
                ))
            elif not right_tool:
                # Tool only in left snapshot (removed)
                diffs.append(ToolDiff(
                    tool_id=tool_id,
                    tool_name=left_tool.get("name", tool_id),
                    version_left=left_tool.get("version", "unknown"),
                    version_right=None,
                    status="removed"
                ))
            elif left_tool.get("version") != right_tool.get("version"):
                # Version changed
                diffs.append(ToolDiff(
                    tool_id=tool_id,
                    tool_name=left_tool.get("name", tool_id),
                    version_left=left_tool.get("version", "unknown"),
                    version_right=right_tool.get("version", "unknown"),
                    status="version_changed"
                ))
            else:
                # Same tool and version
                diffs.append(ToolDiff(
                    tool_id=tool_id,
                    tool_name=left_tool.get("name", tool_id),
                    version_left=left_tool.get("version", "unknown"),
                    version_right=right_tool.get("version", "unknown"),
                    status="same"
                ))
        
        return SnapshotComparison(
            left_name=left.get("name", "Left"),
            right_name=right.get("name", "Right"),
            left_count=len(left_tools),
            right_count=len(right_tools),
            diffs=diffs
        )
    
    @staticmethod
    def print_comparison(comparison: SnapshotComparison):
        """Print the comparison results in a readable format"""
        print(f"\n📊 Environment Comparison")
        print("=" * 60)
        print(f"  Left:  {comparison.left_name} ({comparison.left_count} tools)")
        print(f"  Right: {comparison.right_name} ({comparison.right_count} tools)")
        print("=" * 60)
        
        # Count statuses
        added = [d for d in comparison.diffs if d.status == "added"]
        removed = [d for d in comparison.diffs if d.status == "removed"]
        changed = [d for d in comparison.diffs if d.status == "version_changed"]
        same = [d for d in comparison.diffs if d.status == "same"]
        
        print(f"\n📋 Summary: {comparison.summary}")
        
        if added:
            print(f"\n➕ Added ({len(added)}):")
            for d in added:
                print(f"    {d.tool_name} ({d.tool_id}) -> {d.version_right}")
        
        if removed:
            print(f"\n➖ Removed ({len(removed)}):")
            for d in removed:
                print(f"    {d.tool_name} ({d.tool_id}) <- {d.version_left}")
        
        if changed:
            print(f"\n🔄 Version Changed ({len(changed)}):")
            for d in changed:
                print(f"    {d.tool_name} ({d.tool_id}): {d.version_left} → {d.version_right}")
        
        if same:
            print(f"\n✅ Same ({len(same)}):")
            for d in same:
                print(f"    {d.tool_name} ({d.tool_id}): {d.version_left}")
        
        print("\n" + "=" * 60)


def compare_snapshot_files(left_path: Path, right_path: Path):
    """Compare two snapshot files directly"""
    comparator = SnapshotComparator()
    left = comparator.load_snapshot(left_path)
    right = comparator.load_snapshot(right_path)
    result = comparator.compare_snapshots(left, right)
    comparator.print_comparison(result)
    return result


def compare_snapshot_ids(snapshot_dir: Path, left_id: str, right_id: str):
    """Compare two snapshots by their IDs"""
    left_path = snapshot_dir / f"{left_id}.json"
    right_path = snapshot_dir / f"{right_id}.json"
    
    if not left_path.exists():
        print(f"❌ Snapshot '{left_id}' not found")
        return None
    
    if not right_path.exists():
        print(f"❌ Snapshot '{right_id}' not found")
        return None
    
    return compare_snapshot_files(left_path, right_path)