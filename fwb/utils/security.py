"""
Security utilities - hashing, verification, safe execution
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any


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
        logger.error(
            f"File not found: {file_path}"
        )
        return None

    try:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(
                lambda: f.read(4096),
                b""
            ):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    except Exception as e:
        logger.error(
            f"Error calculating SHA-256: {e}"
        )
        return None


def verify_sha256(
    file_path: Path,
    expected_hash: str
) -> bool:
    """
    Verify that a file's SHA-256 matches the expected hash

    Args:
        file_path: Path to the file
        expected_hash: Expected SHA-256 hash

    Returns:
        True if matches, False otherwise
    """

    actual_hash = calculate_sha256(
        file_path
    )

    if actual_hash is None:
        return False

    # Case-insensitive comparison
    if actual_hash.lower() == expected_hash.lower():

        logger.info(
            f"SHA-256 verification successful: "
            f"{file_path.name}"
        )

        return True

    else:

        logger.error(
            f"SHA-256 mismatch for {file_path.name}"
        )

        logger.error(
            f"Expected: {expected_hash}"
        )

        logger.error(
            f"Actual: {actual_hash}"
        )

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
        # Resolve to absolute path and check
        # it's within allowed directories
        resolved = path.resolve()

        # List of allowed base directories
        allowed_bases = [
            Path.home()
            / "AppData"
            / "Local"
            / "FWB",

            Path.home()
            / "Downloads",

            Path.cwd()
            / "tools",

            Path.cwd()
            / "data",
        ]

        for base in allowed_bases:

            try:
                if resolved.is_relative_to(base):
                    return True

            except ValueError:
                continue

        logger.warning(
            f"Path not in allowed directories: {resolved}"
        )

        return False

    except Exception as e:

        logger.error(
            f"Error checking path safety: {e}"
        )

        return False


def generate_manifest_signature(
    manifest_data: Dict[str, Any]
) -> str:
    """
    Generate a signature for a tool manifest.

    Excludes the 'signature' field itself from the hash.
    """

    # Create a copy without the signature field
    data_copy = {
        k: v
        for k, v in manifest_data.items()
        if k != "signature"
    }

    # Sort keys for consistency
    sorted_data = {
        k: data_copy[k]
        for k in sorted(data_copy.keys())
    }

    # Convert to JSON string with sorted keys
    json_string = json.dumps(
        sorted_data,
        sort_keys=True,
        separators=(',', ':')
    )

    # Generate SHA-256 hash
    return hashlib.sha256(
        json_string.encode()
    ).hexdigest()


def verify_manifest_signature(
    manifest_data: Dict[str, Any]
) -> bool:
    """
    Verify that a manifest's signature matches its content.

    Returns True if valid or if no signature is present
    (legacy mode).
    """

    if "signature" not in manifest_data:
        # No signature - accept as legacy manifest
        return True

    expected = manifest_data["signature"]

    calculated = generate_manifest_signature(
        manifest_data
    )

    return expected == calculated


def sign_manifest(
    manifest_path: Path
) -> bool:
    """
    Add a signature to an existing manifest file.
    """

    try:
        with open(
            manifest_path,
            'r'
        ) as f:

            data = json.load(f)

        # Generate signature
        data["signature"] = generate_manifest_signature(
            data
        )

        # Write back
        with open(
            manifest_path,
            'w'
        ) as f:

            json.dump(
                data,
                f,
                indent=2
            )

        return True

    except Exception as e:

        print(
            f"Failed to sign manifest "
            f"{manifest_path}: {e}"
        )

        return False