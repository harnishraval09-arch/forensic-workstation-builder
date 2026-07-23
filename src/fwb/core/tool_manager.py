"""
Tool Manager - Core orchestration for installing and managing tools
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.tool import Tool, InstallMethod, OSType
from ..utils.security import verify_sha256, calculate_sha256
from ..utils.downloader import Downloader

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
        
        logger.info(f"ToolManager initialized with tools dir: {self.tools_dir}")
    
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
            
            tool = Tool(**data)
            self.tools[tool.id] = tool
            
            # Check if tool is already installed
            install_path = self._get_install_path(tool)
            if install_path.exists():
                tool.installed = True
                tool.install_path = str(install_path)
                self.installed_tools[tool.id] = tool
                logger.info(f"Loaded installed tool: {tool.name}")
            else:
                logger.info(f"Loaded tool: {tool.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load tool from {manifest_path}: {e}")
            return False
    
    def install_tool(self, tool_id: str) -> Tuple[bool, str]:
        """
        Install a tool
        
        Args:
            tool_id: ID of the tool to install
            
        Returns:
            (success, message)
        """
        tool = self.tools.get(tool_id)
        if not tool:
            return False, f"Tool '{tool_id}' not found"
        
        if tool.installed:
            return False, f"Tool '{tool.name}' already installed"
        
        # Check dependencies
        for dep_id in tool.dependencies:
            if dep_id not in self.installed_tools:
                success, msg = self.install_tool(dep_id)
                if not success:
                    return False, f"Dependency '{dep_id}' failed: {msg}"
        
        try:
            logger.info(f"Installing {tool.name} ({tool.version})")
            
            # Determine install method
            install_dir = self._get_install_path(tool)
            install_dir.mkdir(parents=True, exist_ok=True)
            
            if tool.install_method == InstallMethod.INSTALLER.value:
                return self._install_installer(tool)
            elif tool.install_method == InstallMethod.PORTABLE.value:
                return self._install_portable(tool)
            elif tool.install_method == InstallMethod.ARCHIVE.value:
                return self._install_archive(tool)
            else:
                return False, f"Unsupported install method: {tool.install_method}"
                
        except Exception as e:
            logger.error(f"Installation failed for {tool.name}: {e}")
            return False, str(e)
    
    def _install_installer(self, tool: Tool) -> Tuple[bool, str]:
        """Install via installer (.exe, .msi)"""
        try:
            # Download installer
            dest_path = self._download_tool(tool)
            if not dest_path:
                return False, "Download failed"
            
            # Verify hash
            if tool.sha256:
                if not verify_sha256(dest_path, tool.sha256):
                    return False, "SHA-256 verification failed"
            
            # Run installer
            import subprocess
            result = subprocess.run(
                [str(dest_path), "/S"],  # Silent install
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.returncode == 0:
                tool.installed = True
                self.installed_tools[tool.id] = tool
                logger.info(f"Installed {tool.name}")
                return True, f"Installed {tool.name}"
            else:
                return False, f"Installer failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Installation error: {e}"
    
    def _install_portable(self, tool: Tool) -> Tuple[bool, str]:
        """Install portable executable"""
        try:
            dest_path = self._download_tool(tool)
            if not dest_path:
                return False, "Download failed"
            
            # Verify hash
            if tool.sha256:
                if not verify_sha256(dest_path, tool.sha256):
                    return False, "SHA-256 verification failed"
            
            # For portable, we just copy to the tools directory
            install_dir = self._get_install_path(tool)
            shutil.copy(dest_path, install_dir / dest_path.name)
            
            tool.installed = True
            tool.install_path = str(install_dir)
            self.installed_tools[tool.id] = tool
            
            logger.info(f"Installed portable {tool.name}")
            return True, f"Installed {tool.name}"
            
        except Exception as e:
            return False, f"Installation error: {e}"
    
    def _install_archive(self, tool: Tool) -> Tuple[bool, str]:
        """Install from archive (zip, etc.)"""
        # For now, placeholder - we'll implement proper archive extraction later
        return False, "Archive installation not yet implemented"
    
    def _download_tool(self, tool: Tool) -> Optional[Path]:
        """Download a tool"""
        # Determine file name
        if tool.file_name:
            file_name = tool.file_name
        else:
            # Extract from URL
            file_name = tool.download_url.split('/')[-1]
            if not file_name:
                file_name = f"{tool.id}.exe"
        
        dest_path = self.tools_dir / "downloads" / file_name
        
        def progress_callback(downloaded, total):
            percentage = (downloaded / total) * 100 if total > 0 else 0
            logger.debug(f"Download progress: {percentage:.1f}%")
        
        success = self.downloader.download(
            tool.download_url,
            dest_path,
            progress_callback=progress_callback
        )
        
        return dest_path if success else None
    
    def _get_install_path(self, tool: Tool) -> Path:
        """Get the installation path for a tool"""
        return self.tools_dir / "installed" / tool.id
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    def list_tools(self) -> List[Tool]:
        """List all available tools"""
        return list(self.tools.values())
    
    def list_installed(self) -> List[Tool]:
        """List all installed tools"""
        return list(self.installed_tools.values())