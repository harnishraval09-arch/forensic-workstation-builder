"""
Tool Manager - Core orchestration for installing and managing tools
"""

import json
import logging
import shutil
import re  # ← ADDED for version extraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.tool import Tool, InstallMethod, OSType
from ..utils.security import (
    verify_sha256,
    calculate_sha256,
    verify_manifest_signature
)
from ..utils.downloader import Downloader
from ..utils.logger import (
    log_audit,
    log_install_event,
    log_download_event,
    log_verification_event
)


logger = logging.getLogger(__name__)


class ToolManager:
    """Main manager for tool operations"""

    def __init__(self, tools_dir: Optional[Path] = None):
        """
        Initialize the Tool Manager

        Args:
            tools_dir: Directory where tool files are stored
        """
        self.tools_dir = tools_dir or Path("tools")
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        self.downloader = Downloader()
        self.tools: Dict[str, Tool] = {}
        self.installed_tools: Dict[str, Tool] = {}

        logger.info(
            f"ToolManager initialized with tools dir: {self.tools_dir}"
        )

    def load_tool(self, manifest_path: Path) -> bool:
        """
        Load a tool from a manifest file

        Args:
            manifest_path: Path to tool manifest JSON

        Returns:
            True if loaded successfully
        """
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)

            # Verify manifest signature
            if not verify_manifest_signature(data):
                logger.error(
                    f"❌ Manifest signature verification FAILED "
                    f"for {manifest_path}"
                )

                log_audit(
                    "manifest_verification_failed",
                    status="error",
                    details={
                        "manifest": str(manifest_path)
                    }
                )

                return False

            logger.info(
                f"✅ Manifest signature verified "
                f"for {manifest_path.name}"
            )

            # Remove signature before creating Tool object
            data_copy = {
                k: v
                for k, v in data.items()
                if k != "signature"
            }

            tool = Tool(**data_copy)
            self.tools[tool.id] = tool

            # Check if tool is already installed
            install_path = self._get_install_path(tool)

            if install_path.exists():
                tool.installed = True
                tool.install_path = str(install_path)
                self.installed_tools[tool.id] = tool

                logger.info(
                    f"Loaded installed tool: {tool.name}"
                )
            else:
                logger.info(
                    f"Loaded tool: {tool.name}"
                )

            return True

        except Exception as e:
            logger.error(
                f"Failed to load tool from {manifest_path}: {e}"
            )
            return False

    def install_tool(self, tool_id: str) -> Tuple[bool, str]:
        """Install a tool with audit logging"""

        log_audit(
            "install_started",
            tool_id=tool_id,
            status="info"
        )

        tool = self.tools.get(tool_id)

        if not tool:
            log_audit(
                "install_failed",
                tool_id=tool_id,
                status="error",
                details={
                    "reason": f"Tool '{tool_id}' not found"
                }
            )

            return False, f"Tool '{tool_id}' not found"

        if tool.installed:
            log_audit(
                "install_skipped",
                tool_id=tool_id,
                status="warning",
                details={
                    "reason": "Already installed"
                }
            )

            return False, f"Tool '{tool.name}' already installed"

        # Check dependencies
        for dep_id in tool.dependencies:
            if dep_id not in self.installed_tools:

                log_audit(
                    "dependency_check",
                    tool_id=tool_id,
                    status="info",
                    details={
                        "dependency": dep_id
                    }
                )

                success, msg = self.install_tool(dep_id)

                if not success:
                    log_audit(
                        "install_failed",
                        tool_id=tool_id,
                        status="error",
                        details={
                            "reason": (
                                f"Dependency '{dep_id}' failed: {msg}"
                            )
                        }
                    )

                    return False, (
                        f"Dependency '{dep_id}' failed: {msg}"
                    )

        try:
            logger.info(
                f"Installing {tool.name} ({tool.version})"
            )

            install_dir = self._get_install_path(tool)

            install_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # Download first
            download_path = self._download_tool(tool)

            if not download_path:
                log_audit(
                    "install_failed",
                    tool_id=tool_id,
                    status="error",
                    details={
                        "reason": "Download failed"
                    }
                )

                return False, "Download failed"

            # Determine install method
            if tool.install_method == InstallMethod.INSTALLER.value:
                result = self._install_installer(
                    tool,
                    download_path
                )

            elif tool.install_method == InstallMethod.PORTABLE.value:
                result = self._install_portable(
                    tool,
                    download_path
                )

            elif tool.install_method == InstallMethod.ARCHIVE.value:
                result = self._install_archive(
                    tool,
                    download_path
                )

            elif tool.install_method == InstallMethod.PYTHON_PACKAGE.value:
                result = self._install_python_package(tool)

            else:
                result = (
                    False,
                    f"Unsupported install method: {tool.install_method}"
                )

            if result[0]:
                tool.installed = True
                tool.install_path = str(install_dir)
                self.installed_tools[tool.id] = tool

                log_audit(
                    "install_completed",
                    tool_id=tool_id,
                    status="success"
                )

                logger.info(
                    f"✅ Installed {tool.name}"
                )

            else:
                log_audit(
                    "install_failed",
                    tool_id=tool_id,
                    status="error",
                    details={
                        "reason": result[1]
                    }
                )

            return result

        except Exception as e:
            log_audit(
                "install_failed",
                tool_id=tool_id,
                status="error",
                details={
                    "exception": str(e)
                }
            )

            return False, str(e)

    def _install_installer(
        self,
        tool: Tool,
        download_path: Path
    ) -> Tuple[bool, str]:
        """Install via installer (.exe, .msi)"""

        import subprocess
        import platform

        try:
            os_type = platform.system().lower()

            if os_type == "windows":

                if download_path.suffix.lower() == '.msi':
                    args = [
                        'msiexec',
                        '/i',
                        str(download_path),
                        '/quiet',
                        '/norestart'
                    ]

                else:
                    args = [
                        str(download_path),
                        '/S',
                        '/quiet'
                    ]

            else:
                import os

                os.chmod(
                    download_path,
                    0o755
                )

                args = [
                    str(download_path)
                ]

            logger.info(
                f"Running: {' '.join(args)}"
            )

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return True, f"Installed {tool.name}"

            else:
                error_msg = (
                    result.stderr
                    or result.stdout
                    or "Unknown error"
                )

                return False, (
                    f"Installer failed: {error_msg[:200]}"
                )

        except subprocess.TimeoutExpired:
            return False, (
                "Installation timed out after 10 minutes"
            )

        except Exception as e:
            return False, (
                f"Installation error: {str(e)}"
            )

    def _install_portable(
        self,
        tool: Tool,
        download_path: Path
    ) -> Tuple[bool, str]:
        """Install portable executable"""

        import shutil
        import os

        try:
            install_dir = self._get_install_path(tool)

            install_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            dest_path = install_dir / download_path.name

            shutil.copy2(
                download_path,
                dest_path
            )

            if os.name != 'nt':
                os.chmod(
                    dest_path,
                    0o755
                )

            return True, (
                f"Installed {tool.name} to {install_dir}"
            )

        except Exception as e:
            return False, (
                f"Installation error: {str(e)}"
            )

    def _install_archive(
        self,
        tool: Tool,
        download_path: Path
    ) -> Tuple[bool, str]:
        """Install from archive (zip, tar.gz, etc.)"""

        import zipfile
        import tarfile

        try:
            install_dir = self._get_install_path(tool)

            install_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            if download_path.suffix.lower() == '.zip':

                with zipfile.ZipFile(
                    download_path,
                    'r'
                ) as zip_ref:

                    zip_ref.extractall(
                        install_dir
                    )

                logger.info(
                    f"Extracted ZIP to {install_dir}"
                )

            else:

                with tarfile.open(
                    download_path,
                    'r:*'
                ) as tar_ref:

                    tar_ref.extractall(
                        install_dir
                    )

                logger.info(
                    f"Extracted archive to {install_dir}"
                )

            return True, (
                f"Extracted {tool.name} to {install_dir}"
            )

        except Exception as e:
            return False, (
                f"Extraction error: {str(e)}"
            )

    def _install_python_package(
        self,
        tool: Tool
    ) -> Tuple[bool, str]:
        """Install Python package via pip"""

        import subprocess

        try:
            package_name = (
                tool.file_name
                or tool.id
            )

            result = subprocess.run(
                [
                    'pip',
                    'install',
                    package_name
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True, (
                    f"Installed {tool.name} via pip"
                )

            else:
                return False, (
                    f"pip install failed: "
                    f"{result.stderr[:200]}"
                )

        except Exception as e:
            return False, (
                f"pip install error: {str(e)}"
            )

    def _download_tool(
        self,
        tool: Tool
    ) -> Optional[Path]:
        """Download a tool with audit logging and version validation"""

        if tool.file_name:
            file_name = tool.file_name

        else:
            file_name = (
                tool.download_url.split('/')[-1]
            )

            if not file_name:
                file_name = f"{tool.id}.exe"

        dest_path = (
            self.tools_dir
            / "downloads"
            / file_name
        )

        def progress_callback(downloaded, total):
            percentage = (
                (downloaded / total) * 100
                if total > 0
                else 0
            )

            logger.debug(
                f"Download progress: {percentage:.1f}%"
            )

        success = self.downloader.download(
            tool.download_url,
            dest_path,
            progress_callback=progress_callback
        )

        if success:

            size = (
                dest_path.stat().st_size
                if dest_path.exists()
                else 0
            )

            log_download_event(
                tool.id,
                tool.download_url,
                True,
                size
            )

            # ============================================
            # NEW: Version Validation (Fixes Issue #2)
            # ============================================
            if tool.version:
                extracted_version = self._extract_version_from_file(dest_path)
                if extracted_version and extracted_version != tool.version:
                    log_audit(
                        "version_mismatch",
                        tool_id=tool.id,
                        status="warning",
                        details={
                            "expected": tool.version,
                            "actual": extracted_version
                        }
                    )
                    logger.warning(
                        f"Version mismatch for {tool.name}: "
                        f"expected {tool.version}, got {extracted_version}"
                    )
                elif extracted_version:
                    logger.info(
                        f"✅ Version verified for {tool.name}: "
                        f"{extracted_version} matches {tool.version}"
                    )

            if tool.sha256:

                verified = verify_sha256(
                    dest_path,
                    tool.sha256
                )

                log_verification_event(
                    tool.id,
                    verified,
                    tool.sha256
                )

                if not verified:
                    return None

        else:

            log_download_event(
                tool.id,
                tool.download_url,
                False
            )

        return (
            dest_path
            if success
            else None
        )

    # ============================================
    # NEW: Helper method for version extraction (Fixes Issue #2)
    # ============================================
    def _extract_version_from_file(self, file_path: Path) -> Optional[str]:
        """
        Extract version from downloaded file name.
        Looks for patterns like "4.6.7" or "v10.18.0" in the filename.
        """
        try:
            # Look for version pattern in filename
            # Matches: 4.6.7, 10.18.0, 12.1.2, etc.
            match = re.search(r'[\d]+\.[\d]+\.?[\d]*', file_path.name)
            if match:
                return match.group(0)
            
            # Also try to find version in the file name with 'v' prefix
            match = re.search(r'v([\d]+\.[\d]+\.?[\d]*)', file_path.name)
            if match:
                return match.group(1)
            
            return None
        except Exception as e:
            logger.debug(f"Could not extract version from {file_path.name}: {e}")
            return None

    def _get_install_path(
        self,
        tool: Tool
    ) -> Path:
        """Get the installation path for a tool"""

        return (
            self.tools_dir
            / "installed"
            / tool.id
        )

    def get_tool(
        self,
        tool_id: str
    ) -> Optional[Tool]:
        """Get a tool by ID"""

        return self.tools.get(tool_id)

    def list_tools(self) -> List[Tool]:
        """List all available tools"""

        return list(
            self.tools.values()
        )

    def list_installed(self) -> List[Tool]:
        """List all installed tools"""

        return list(
            self.installed_tools.values()
        )

    def uninstall_tool(
        self,
        tool_id: str
    ) -> Tuple[bool, str]:
        """Uninstall a tool"""

        import shutil

        tool = self.tools.get(tool_id)

        if not tool:
            return False, (
                f"Tool '{tool_id}' not found"
            )

        if not tool.installed:
            return False, (
                f"Tool '{tool.name}' is not installed"
            )

        try:
            install_path = (
                Path(tool.install_path)
                if tool.install_path
                else self._get_install_path(tool)
            )

            if install_path.exists():
                shutil.rmtree(
                    install_path
                )

            tool.installed = False
            tool.install_path = None

            if tool.id in self.installed_tools:
                del self.installed_tools[tool.id]

            log_audit(
                "uninstall_completed",
                tool_id=tool_id,
                status="success"
            )

            return True, (
                f"Uninstalled {tool.name}"
            )

        except Exception as e:

            log_audit(
                "uninstall_failed",
                tool_id=tool_id,
                status="error",
                details={
                    "exception": str(e)
                }
            )

            return False, (
                f"Uninstall error: {str(e)}"
            )

    def pin_version(
        self,
        tool_id: str,
        version: str,
        hash_value: str = ""
    ):
        """Pin a specific version and hash for a tool"""

        tool = self.tools.get(tool_id)

        if tool:
            tool.pinned_version = version
            tool.pinned_hash = hash_value

            logger.info(
                f"Pinned {tool.name} to version {version}"
            )

            return True

        return False