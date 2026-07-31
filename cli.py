"""
Forensic Workstation Builder - Command Line Interface

Usage:
    python cli.py install <tool_id>
    python cli.py list [--installed]
    python cli.py install-profile <profile_id>
    python cli.py list-profiles
    python cli.py create-snapshot <name> [--description <desc>]
    python cli.py compare <left_id> <right_id>
    python cli.py info <tool_id>
    python cli.py --help

@author: Harnish Raval
"""

import sys
import logging
from pathlib import Path
import argparse
import json

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "fwb"))

from fwb.core.tool_manager import ToolManager
from fwb.core.profile_manager import ProfileManager
from fwb.core.dependency_resolver import DependencyResolver
from fwb.core.installer import Installer
from fwb.utils.logger import log_audit

# Suppress debug logging for CLI
logging.basicConfig(level=logging.WARNING)


def setup_backend():
    """Initialize backend managers"""
    data_dir = ROOT_DIR / "data"

    tool_manager = ToolManager(tools_dir=data_dir)

    for manifest_path in sorted((data_dir / "tools").glob("*.json")):
        tool_manager.load_tool(manifest_path)

    profile_manager = ProfileManager(
        profiles_dir=data_dir / "profiles"
    )

    dependency_resolver = DependencyResolver()
    installer = Installer()

    return (
        tool_manager,
        profile_manager,
        dependency_resolver,
        installer
    )


def print_tool_info(tool, installed=False):
    """Print tool information in a readable format"""

    status = (
        "✅ INSTALLED"
        if installed
        else "⬜ NOT INSTALLED"
    )

    print(f"  {tool.name} ({tool.id})")
    print(f"    Version: {tool.version}")
    print(f"    Category: {tool.category}")
    print(f"    Status: {status}")

    if tool.dependencies:
        print(
            f"    Dependencies: "
            f"{', '.join(tool.dependencies)}"
        )

    print()


def cmd_list(tool_manager, args):
    """List all available tools"""

    tools = tool_manager.list_tools()
    installed = tool_manager.list_installed()

    installed_ids = {
        t.id
        for t in installed
    }

    if args.installed:

        print(
            f"\n📦 Installed Tools "
            f"({len(installed)}):"
        )

        print("-" * 50)

        if installed:

            for tool in installed:
                print(
                    f"  ✅ {tool.name} "
                    f"v{tool.version}"
                )

        else:
            print(
                "  No tools installed yet."
            )

        return

    print(
        f"\n📦 Available Tools "
        f"({len(tools)}):"
    )

    print("-" * 50)

    for tool in sorted(
        tools,
        key=lambda t: t.name
    ):

        status = (
            "✅"
            if tool.id in installed_ids
            else "⬜"
        )

        print(
            f"  {status} "
            f"{tool.name} "
            f"({tool.id}) "
            f"- v{tool.version}"
        )

    print()


def cmd_install(tool_manager, args):
    """Install a tool"""

    tool_id = args.tool_id

    print(
        f"\n🔧 Installing {tool_id}..."
    )

    print("-" * 50)

    success, message = (
        tool_manager.install_tool(tool_id)
    )

    if success:

        print(
            f"✅ {message}"
        )

        log_audit(
            "cli_install_success",
            tool_id=tool_id,
            status="success"
        )

    else:

        print(
            f"❌ {message}"
        )

        log_audit(
            "cli_install_failed",
            tool_id=tool_id,
            status="error",
            details={
                "reason": message
            }
        )

        sys.exit(1)


def cmd_install_profile(
    profile_manager,
    tool_manager,
    args
):
    """Install an entire profile"""

    profile_id = args.profile_id

    profile = (
        profile_manager
        .get_profile(profile_id)
    )

    if not profile:

        print(
            f"❌ Profile "
            f"'{profile_id}' "
            f"not found"
        )

        sys.exit(1)

    print(
        f"\n📋 Installing Profile: "
        f"{profile.name}"
    )

    print("-" * 50)

    print(
        f"Tools: "
        f"{', '.join(profile.tools)}"
    )

    print()

    results = []

    for tool_id in profile.tools:

        print(
            f"  Installing "
            f"{tool_id}..."
        )

        success, message = (
            tool_manager
            .install_tool(tool_id)
        )

        results.append(
            (
                tool_id,
                success,
                message
            )
        )

        if success:

            print(
                f"    ✅ {message}"
            )

        else:

            print(
                f"    ❌ {message}"
            )

    print(
        "\n"
        + "-"
        * 50
    )

    success_count = sum(
        1
        for _, success, _
        in results
        if success
    )

    total = len(results)

    if success_count == total:

        print(
            f"✅ Profile "
            f"'{profile.name}' "
            f"installed successfully!"
        )

    else:

        print(
            f"⚠️ Installed "
            f"{success_count}/{total} tools."
        )


def cmd_list_profiles(
    profile_manager,
    args
):
    """List all available profiles"""

    profiles = (
        profile_manager
        .list_profiles()
    )

    if not profiles:

        print(
            "❌ No profiles found."
        )

        return

    print(
        f"\n📋 Available Profiles "
        f"({len(profiles)}):"
    )

    print("-" * 50)

    for profile in sorted(
        profiles,
        key=lambda p: p.name
    ):

        print(
            f"  📦 "
            f"{profile.name} "
            f"({profile.id})"
        )

        print(
            f"    Category: "
            f"{profile.category}"
        )

        print(
            f"    Tools: "
            f"{', '.join(profile.tools)}"
        )

        print()


def cmd_create_snapshot(
    tool_manager,
    args
):
    """Create an environment snapshot"""

    name = args.name

    description = (
        args.description
        or ""
    )

    installed = (
        tool_manager
        .list_installed()
    )

    if not installed:

        print(
            "❌ No tools installed. "
            "Nothing to snapshot."
        )

        sys.exit(1)

    snapshot = {

        "id": (
            f"snapshot_"
            f"{name.replace(' ', '_')}"
        ),

        "name": name,

        "description": description,

        "tools": [

            {
                "id": tool.id,
                "name": tool.name,
                "version": tool.version,

                "pinned_version": getattr(
                    tool,
                    'pinned_version',
                    tool.version
                ),

                "pinned_hash": getattr(
                    tool,
                    'pinned_hash',
                    ""
                )
            }

            for tool in installed
        ]
    }

    # Save snapshot
    snapshot_dir = (
        ROOT_DIR
        / "data"
        / "snapshots"
    )

    snapshot_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        snapshot_dir
        / f"{snapshot['id']}.json"
    )

    with open(file_path, 'w') as f:

        json.dump(
            snapshot,
            f,
            indent=2
        )

    log_audit(
        "cli_snapshot_created",
        status="success",
        details={
            "snapshot_name": name,
            "tool_count": len(installed)
        }
    )

    print(
        "\n📸 Snapshot Created!"
    )

    print("-" * 50)

    print(
        f"  Name: {name}"
    )

    print(
        f"  Tools: "
        f"{len(installed)}"
    )

    print(
        f"  Saved to: "
        f"{file_path}"
    )


def cmd_compare(args):
    """Compare two snapshots"""

    from fwb.utils.snapshot_comparator import (
        compare_snapshot_ids
    )

    snapshot_dir = (
        ROOT_DIR
        / "data"
        / "snapshots"
    )

    compare_snapshot_ids(
        snapshot_dir,
        args.left_id,
        args.right_id
    )


def cmd_info(
    tool_manager,
    args
):
    """Show detailed information about a tool"""

    tool_id = args.tool_id

    tool = (
        tool_manager
        .get_tool(tool_id)
    )

    if not tool:

        print(
            f"❌ Tool "
            f"'{tool_id}' "
            f"not found"
        )

        sys.exit(1)

    installed = (
        tool.id
        in tool_manager.installed_tools
    )

    print(
        f"\n📄 Tool: "
        f"{tool.name}"
    )

    print("-" * 50)

    print(
        f"  ID: "
        f"{tool.id}"
    )

    print(
        f"  Version: "
        f"{tool.version}"
    )

    print(
        f"  Category: "
        f"{tool.category}"
    )

    print(
        f"  Description: "
        f"{tool.description}"
    )

    print(
        f"  Status: "
        f"{'✅ Installed' if installed else '⬜ Not Installed'}"
    )

    print(
        f"  Install Method: "
        f"{tool.install_method}"
    )

    print(
        f"  Supported OS: "
        f"{', '.join(tool.supported_os)}"
    )

    if tool.dependencies:

        print(
            f"  Dependencies: "
            f"{', '.join(tool.dependencies)}"
        )

    if tool.requires_admin:

        print(
            "  ⚠️ Requires Administrator"
        )

    if tool.install_path and installed:

        print(
            f"  Install Path: "
            f"{tool.install_path}"
        )

    if tool.pinned_version:

        print(
            f"  Pinned Version: "
            f"{tool.pinned_version}"
        )

    print()


def main():

    parser = argparse.ArgumentParser(

        description=(
            "Forensic Workstation "
            "Builder - CLI"
        ),

        formatter_class=(
            argparse
            .RawDescriptionHelpFormatter
        ),

        epilog="""
Examples:
  python cli.py list
  python cli.py list --installed
  python cli.py install wireshark
  python cli.py install-profile "Windows Forensics"
  python cli.py list-profiles
  python cli.py create-snapshot "My Lab"
  python cli.py compare snapshot_one snapshot_two
  python cli.py info wireshark
        """
    )

    subparsers = (
        parser
        .add_subparsers(
            dest="command",
            help="Available commands"
        )
    )

    # List command
    list_parser = (
        subparsers
        .add_parser(
            "list",
            help="List tools"
        )
    )

    list_parser.add_argument(
        "--installed",
        action="store_true",
        help="Show installed tools only"
    )

    # Install command
    install_parser = (
        subparsers
        .add_parser(
            "install",
            help="Install a tool"
        )
    )

    install_parser.add_argument(
        "tool_id",
        help="Tool ID to install"
    )

    # Install profile command
    profile_parser = (
        subparsers
        .add_parser(
            "install-profile",
            help="Install a profile"
        )
    )

    profile_parser.add_argument(
        "profile_id",
        help="Profile ID to install"
    )

    # List profiles command
    subparsers.add_parser(
        "list-profiles",
        help="List available profiles"
    )

    # Create snapshot command
    snapshot_parser = (
        subparsers
        .add_parser(
            "create-snapshot",
            help="Create a snapshot"
        )
    )

    snapshot_parser.add_argument(
        "name",
        help="Snapshot name"
    )

    snapshot_parser.add_argument(
        "--description",
        help="Snapshot description"
    )

    # Compare command
    compare_parser = (
        subparsers
        .add_parser(
            "compare",
            help="Compare two snapshots"
        )
    )

    compare_parser.add_argument(
        "left_id",
        help="First snapshot ID"
    )

    compare_parser.add_argument(
        "right_id",
        help="Second snapshot ID"
    )

    # Info command
    info_parser = (
        subparsers
        .add_parser(
            "info",
            help="Show tool details"
        )
    )

    info_parser.add_argument(
        "tool_id",
        help="Tool ID"
    )

    args = parser.parse_args()

    if not args.command:

        parser.print_help()

        sys.exit(1)

    # Compare does not require the full backend setup
    if args.command == "compare":

        cmd_compare(args)

        return

    # Setup backend
    (
        tool_manager,
        profile_manager,
        _,
        _
    ) = setup_backend()

    # Route command
    if args.command == "list":

        cmd_list(
            tool_manager,
            args
        )

    elif args.command == "install":

        cmd_install(
            tool_manager,
            args
        )

    elif args.command == "install-profile":

        cmd_install_profile(
            profile_manager,
            tool_manager,
            args
        )

    elif args.command == "list-profiles":

        cmd_list_profiles(
            profile_manager,
            args
        )

    elif args.command == "create-snapshot":

        cmd_create_snapshot(
            tool_manager,
            args
        )

    elif args.command == "info":

        cmd_info(
            tool_manager,
            args
        )

    else:

        print(
            f"❌ Unknown command: "
            f"{args.command}"
        )

        sys.exit(1)


if __name__ == "__main__":

    main()
