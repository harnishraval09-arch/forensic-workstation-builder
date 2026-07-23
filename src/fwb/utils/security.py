"""
Security utilities - hashing, verification, safe execution
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def calculate_sha256(file_path: Path) -> Optional[str]:
    """
    Calculate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash as hex string, or None if file doesn't exist
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating SHA-256: {e}")
        return None

def verify_sha256(file_path: Path, expected_hash: str) -> bool:
    """
    Verify that a file's SHA-256 matches the expected hash
    
    Args:
        file_path: Path to the file
        expected_hash: Expected SHA-256 hash
        
    Returns:
        True if matches, False otherwise
    """
    actual_hash = calculate_sha256(file_path)
    if actual_hash is None:
        return False
    
    # Case-insensitive comparison
    if actual_hash.lower() == expected_hash.lower():
        logger.info(f"SHA-256 verification successful: {file_path.name}")
        return True
    else:
        logger.error(f"SHA-256 mismatch for {file_path.name}")
        logger.error(f"Expected: {expected_hash}")
        logger.error(f"Actual: {actual_hash}")
        return False

def is_safe_path(path: Path) -> bool:
    """
    Check if a path is safe to use (prevents path traversal)
    
    Args:
        path: Path to check
        
    Returns:
        True if safe, False otherwise
    """
    try:
        # Resolve to absolute path and check it's within allowed directories
        resolved = path.resolve()
        
        # List of allowed base directories
        allowed_bases = [
            Path.home() / "AppData" / "Local" / "FWB",
            Path.home() / "Downloads",
            Path.cwd() / "tools",
            Path.cwd() / "data",
        ]
        
        for base in allowed_bases:
            try:
                if resolved.is_relative_to(base):
                    return True
            except ValueError:
                continue
        
        logger.warning(f"Path not in allowed directories: {resolved}")
        return False
        
    except Exception as e:
        logger.error(f"Error checking path safety: {e}")
        return False