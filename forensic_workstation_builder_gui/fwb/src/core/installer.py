"""
Installation handlers for different tool types
"""

import logging
import subprocess
import shutil
import zipfile
import os
from pathlib import Path
from typing import Tuple, Optional, Callable
import platform

from ..models.tool import Tool, InstallMethod

logger = logging.getLogger(__name__)

class Installer:
    """Handles different installation methods"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        logger.info(f"Installer initialized for OS: {self.os_type}")
    
    def install_tool(
        self, 
        tool: Tool, 
        download_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """
        Install a tool based on its install method
        
        Args:
            tool: Tool to install
            download_path: Path where file was downloaded
            progress_callback: Callback for progress updates
            
        Returns:
            (success, message)
        """
        if progress_callback:
            progress_callback(f"Installing {tool.name}...", 50)
        
        if tool.install_method == InstallMethod.INSTALLER.value:
            return self._install_installer(tool, download_path, progress_callback)
        elif tool.install_method == InstallMethod.PORTABLE.value:
            return self._install_portable(tool, download_path, progress_callback)
        elif tool.install_method == InstallMethod.ARCHIVE.value:
            return self._install_archive(tool, download_path, progress_callback)
        elif tool.install_method == InstallMethod.PYTHON_PACKAGE.value:
            return self._install_python_package(tool, progress_callback)
        else:
            return False, f"Unsupported install method: {tool.install_method}"
    
    def _install_installer(
        self, 
        tool: Tool, 
        download_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """Install via installer (.exe, .msi)"""
        try:
            if progress_callback:
                progress_callback("Running installer...", 70)
            
            # Determine silent install arguments based on OS
            if self.os_type == "windows":
                if download_path.suffix.lower() == '.msi':
                    args = ['msiexec', '/i', str(download_path), '/quiet', '/norestart']
                else:
                    args = [str(download_path), '/S', '/quiet']
            else:
                # Linux - make executable and run
                os.chmod(download_path, 0o755)
                args = [str(download_path)]
            
            logger.info(f"Running: {' '.join(args)}")
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(f"✅ {tool.name} installed successfully!", 100)
                return True, f"Installed {tool.name}"
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"Installer failed: {error_msg[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out after 10 minutes"
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_portable(
        self, 
        tool: Tool, 
        download_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """Install portable executable"""
        try:
            if progress_callback:
                progress_callback(f"Installing {tool.name}...", 70)
            
            # Create install directory
            install_dir = Path(tool.install_path) if tool.install_path else Path(f"tools/installed/{tool.id}")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            dest_path = install_dir / download_path.name
            shutil.copy2(download_path, dest_path)
            
            # Make executable on Unix
            if self.os_type in ["linux", "darwin"]:
                os.chmod(dest_path, 0o755)
            
            if progress_callback:
                progress_callback(f"✅ {tool.name} installed!", 100)
            
            return True, f"Installed {tool.name} to {install_dir}"
            
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_archive(
        self, 
        tool: Tool, 
        download_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """Install from archive (zip, tar.gz, etc.)"""
        try:
            if progress_callback:
                progress_callback(f"Extracting {tool.name}...", 70)
            
            # Create install directory
            install_dir = Path(tool.install_path) if tool.install_path else Path(f"tools/installed/{tool.id}")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract based on file type
            if download_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
                logger.info(f"Extracted ZIP to {install_dir}")
            else:
                # For .tar.gz, .tar.bz2, etc.
                import tarfile
                with tarfile.open(download_path, 'r:*') as tar_ref:
                    tar_ref.extractall(install_dir)
                logger.info(f"Extracted archive to {install_dir}")
            
            if progress_callback:
                progress_callback(f"✅ {tool.name} extracted!", 100)
            
            return True, f"Extracted {tool.name} to {install_dir}"
            
        except Exception as e:
            return False, f"Extraction error: {str(e)}"
    
    def _install_python_package(
        self, 
        tool: Tool,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[bool, str]:
        """Install Python package via pip"""
        try:
            if progress_callback:
                progress_callback(f"Installing {tool.name} via pip...", 70)
            
            # Use the package name from the tool
            package_name = tool.file_name or tool.id
            
            result = subprocess.run(
                ['pip', 'install', package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(f"✅ {tool.name} installed!", 100)
                return True, f"Installed {tool.name} via pip"
            else:
                return False, f"pip install failed: {result.stderr[:200]}"
                
        except Exception as e:
            return False, f"pip install error: {str(e)}"
    
    def uninstall_tool(self, tool: Tool) -> Tuple[bool, str]:
        """Uninstall a tool"""
        try:
            if tool.install_path:
                install_path = Path(tool.install_path)
                if install_path.exists():
                    shutil.rmtree(install_path)
                    return True, f"Uninstalled {tool.name}"
            
            return False, f"No installation found for {tool.name}"
            
        except Exception as e:
            return False, f"Uninstall error: {str(e)}"