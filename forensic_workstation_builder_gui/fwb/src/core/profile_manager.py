"""
Profile management for predefined tool bundles
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from ..models.profile import Profile

logger = logging.getLogger(__name__)

class ProfileManager:
    """Manages forensic environment profiles"""
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        self.profiles_dir = profiles_dir or Path("src/profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles: Dict[str, Profile] = {}
        
        # Load default profiles
        self._load_default_profiles()
        logger.info(f"ProfileManager initialized with {len(self.profiles)} profiles")
    
    def _load_default_profiles(self):
        """Load default profiles from JSON files"""
        if self.profiles_dir.exists():
            for file_path in self.profiles_dir.glob("*.json"):
                self.load_profile(file_path)
    
    def load_profile(self, file_path: Path) -> Optional[Profile]:
        """Load a profile from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            profile = Profile(
                id=data.get('id', file_path.stem),
                name=data.get('name', file_path.stem),
                description=data.get('description', ''),
                tools=data.get('tools', []),
                category=data.get('category', 'General'),
                version=data.get('version', '1.0.0')
            )
            
            self.profiles[profile.id] = profile
            logger.info(f"Loaded profile: {profile.name}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load profile {file_path}: {e}")
            return None
    
    def create_profile(self, profile: Profile) -> bool:
        """Create a new profile"""
        try:
            file_path = self.profiles_dir / f"{profile.id}.json"
            with open(file_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
            
            self.profiles[profile.id] = profile
            logger.info(f"Created profile: {profile.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            return False
    
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID"""
        return self.profiles.get(profile_id)
    
    def list_profiles(self) -> List[Profile]:
        """List all available profiles"""
        return list(self.profiles.values())
    
    def get_profiles_by_category(self, category: str) -> List[Profile]:
        """Get profiles by category"""
        return [p for p in self.profiles.values() if p.category == category]