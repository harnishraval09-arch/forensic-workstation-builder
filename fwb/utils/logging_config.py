"""
Dynamic logging configuration for Forensic Workstation Builder
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def setup_logging(level=logging.INFO):
    """Setup logging with the specified level"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("fwb")


def set_log_level(level_name: str):
    """Set log level dynamically"""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.getLogger("fwb").setLevel(level)
    logging.info(f"Log level set to {level_name.upper()}")