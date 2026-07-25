"""
Forensic Workstation Builder - GUI entry point.
"""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

ROOT_DIR = Path(__file__).resolve().parent

# All imports now use fwb (not src)
from fwb.core.tool_manager import ToolManager
from fwb.core.profile_manager import ProfileManager
from fwb.core.dependency_resolver import DependencyResolver
from fwb.core.installer import Installer

from fwb.gui.app_state import AppState
from fwb.gui.main_window import MainWindow
from fwb.gui.theme import build_stylesheet

DATA_DIR = ROOT_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def bootstrap_backend():
    tool_manager = ToolManager(tools_dir=DATA_DIR)
    for manifest_path in sorted((DATA_DIR / "tools").glob("*.json")):
        tool_manager.load_tool(manifest_path)

    profile_manager = ProfileManager(profiles_dir=DATA_DIR / "profiles")
    dependency_resolver = DependencyResolver()
    installer = Installer()

    return tool_manager, profile_manager, dependency_resolver, installer


def main():
    setup_logging()
    logger = logging.getLogger("fwb.gui")
    logger.info("Starting Forensic Workstation Builder GUI")

    tool_manager, profile_manager, dependency_resolver, installer = bootstrap_backend()
    logger.info(f"Loaded {len(tool_manager.tools)} tools and {len(profile_manager.profiles)} profiles")

    app = QApplication(sys.argv)
    app.setApplicationName("Forensic Workstation Builder")
    app.setOrganizationName("ForensicWorkstationBuilder")

    app_state = AppState(tool_manager, profile_manager, dependency_resolver, installer, DATA_DIR)
    app_state.log_file = LOG_FILE

    settings = QSettings("ForensicWorkstationBuilder", "FWB-GUI")
    theme = settings.value("theme", "dark")
    app.setStyleSheet(build_stylesheet(theme))

    window = MainWindow(app, app_state)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()