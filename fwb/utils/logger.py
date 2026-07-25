"""
Enhanced audit logging for Forensic Workstation Builder
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Setup main logger
logger = logging.getLogger("fwb")

# Setup audit logger (separate file for audit trail)
audit_logger = logging.getLogger("fwb.audit")
audit_logger.setLevel(logging.INFO)

# Audit log file handler
audit_file = Path("data/logs/audit.log")
audit_file.parent.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(audit_file, encoding="utf-8")
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
audit_logger.addHandler(file_handler)
audit_logger.propagate = False


def log_audit(
    action: str,
    tool_id: Optional[str] = None,
    status: str = "info",
    details: Optional[Dict[str, Any]] = None,
    user: str = "system"
):
    """
    Log an audit event.
    
    Args:
        action: What happened (e.g., "install_started", "hash_verified")
        tool_id: Tool ID if applicable
        status: "info", "success", "warning", "error"
        details: Additional details as dict
        user: User who performed the action
    """
    log_entry = {
        "action": action,
        "user": user,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    if tool_id:
        log_entry["tool_id"] = tool_id
    
    # Log to audit file
    audit_logger.info(json.dumps(log_entry))
    
    # Also log to main logger with appropriate level
    msg = f"AUDIT: {action}"
    if tool_id:
        msg += f" | Tool: {tool_id}"
    if details:
        msg += f" | {details}"
    
    if status == "error":
        logger.error(msg)
    elif status == "warning":
        logger.warning(msg)
    elif status == "success":
        logger.info(f"✅ {msg}")
    else:
        logger.info(msg)


def log_install_event(tool_id: str, event: str, success: bool, details: Dict = None):
    """Helper for installation events"""
    status = "success" if success else "error"
    log_audit(
        action=f"install_{event}",
        tool_id=tool_id,
        status=status,
        details=details or {}
    )


def log_download_event(tool_id: str, url: str, success: bool, size: int = 0):
    """Helper for download events"""
    log_audit(
        action="download",
        tool_id=tool_id,
        status="success" if success else "error",
        details={
            "url": url,
            "size_bytes": size,
            "success": success
        }
    )


def log_verification_event(tool_id: str, verified: bool, expected_hash: str, actual_hash: str = ""):
    """Helper for hash verification events"""
    log_audit(
        action="hash_verify",
        tool_id=tool_id,
        status="success" if verified else "error",
        details={
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
            "verified": verified
        }
    )


def log_snapshot_event(action: str, snapshot_name: str, success: bool):
    """Helper for snapshot events"""
    log_audit(
        action=f"snapshot_{action}",
        tool_id=None,
        status="success" if success else "error",
        details={"snapshot_name": snapshot_name}
    )