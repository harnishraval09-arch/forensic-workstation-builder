"""
Tool data model representing a forensic/security tool
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

class InstallMethod(Enum):
    """Supported installation methods"""
    INSTALLER = "installer"      # .exe, .msi
    PORTABLE = "portable"        # Portable EXE
    ARCHIVE = "archive"          # .zip, .7z
    PYTHON_PACKAGE = "pip"       # pip install
    SCRIPT = "script"            # Custom script
    PACKAGE_MANAGER = "package"  # winget, apt

class OSType(Enum):
    """Supported operating systems"""
    WINDOWS = "windows"
    LINUX = "linux"
    WSL = "wsl"
    MACOS = "macos"

@dataclass
class Tool:
    """
    Represents a tool that can be installed by the system
    """
    # Required fields (NO defaults)
    id: str
    name: str
    description: str
    category: str
    version: str
    supported_os: List[str]
    install_method: str
    download_url: str
    
    # Optional fields (WITH defaults)
    sha256: Optional[str] = None
    dependencies: List[str] = None
    file_name: Optional[str] = None
    install_args: List[str] = None
    requires_admin: bool = False
    source: str = "official"
    documentation_url: Optional[str] = None
    
    # Runtime status (WITH defaults)
    installed: bool = False
    installed_version: Optional[str] = None
    install_path: Optional[str] = None
    
    # Version pinning (WITH defaults)
    pinned_version: Optional[str] = None
    pinned_hash: Optional[str] = None
    
    def __post_init__(self):
        """Initialize optional fields"""
        if self.dependencies is None:
            self.dependencies = []
        if self.install_args is None:
            self.install_args = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "supported_os": self.supported_os,
            "install_method": self.install_method,
            "download_url": self.download_url,
            "sha256": self.sha256,
            "dependencies": self.dependencies,
            "file_name": self.file_name,
            "requires_admin": self.requires_admin,
            "source": self.source,
            "documentation_url": self.documentation_url,
            "pinned_version": self.pinned_version,
            "pinned_hash": self.pinned_hash
        }