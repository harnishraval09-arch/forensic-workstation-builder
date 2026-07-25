"""
Profile model for forensic environment bundles
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Profile:
    """Represents a forensic environment profile"""
    
    id: str
    name: str
    description: str
    tools: List[str]  # List of tool IDs
    category: str = "General"
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "category": self.category,
            "version": self.version
        }