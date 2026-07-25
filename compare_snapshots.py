#!/usr/bin/env python3
"""
Compare two environment snapshots

Usage:
    python compare_snapshots.py <snapshot1.json> <snapshot2.json>
    python compare_snapshots.py --ids snapshot_1 snapshot_2
"""

import sys
from pathlib import Path

# Add project to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "fwb"))

from fwb.utils.snapshot_comparator import compare_snapshot_files, compare_snapshot_ids


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare two forensic environment snapshots")
    parser.add_argument("--ids", nargs=2, metavar=("ID1", "ID2"), 
                        help="Compare snapshots by their IDs")
    parser.add_argument("files", nargs="*", metavar="FILE", 
                        help="Path to two snapshot JSON files")
    
    args = parser.parse_args()
    
    snapshot_dir = ROOT_DIR / "data" / "snapshots"
    
    if args.ids:
        compare_snapshot_ids(snapshot_dir, args.ids[0], args.ids[1])
    elif len(args.files) == 2:
        compare_snapshot_files(Path(args.files[0]), Path(args.files[1]))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()