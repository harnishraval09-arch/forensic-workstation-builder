"""
File downloader with progress tracking
"""

import logging
import requests
from pathlib import Path
from typing import Optional, Callable
import time

logger = logging.getLogger(__name__)

class Downloader:
    """Handles file downloads with progress reporting"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ForensicWorkstationBuilder/0.1.0'
        })
    
    def download(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        timeout: int = 300
    ) -> bool:
        """
        Download a file with progress tracking
        
        Args:
            url: URL to download from
            destination: Where to save the file
            progress_callback: Function called with (downloaded, total)
            timeout: Timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading from: {url}")
            
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Stream download
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Write to file
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"Download complete: {destination.name} ({downloaded} bytes)")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected download error: {e}")
            return False