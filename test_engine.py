"""
Test the Tool Manager
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fwb.core.tool_manager import ToolManager

def test_tool_manager():
    print("=== Testing Tool Manager ===\n")
    
    # Create manager
    manager = ToolManager()
    
    # Load CyberChef
    manifest_path = Path("src/tools/cyberchef.json")
    if manifest_path.exists():
        print("Loading CyberChef manifest...")
        manager.load_tool(manifest_path)
        print(f"✅ Loaded: {manager.get_tool('cyberchef').name}")
    else:
        print(f"❌ Manifest not found: {manifest_path}")
        return
    
    # List available tools
    print(f"\nAvailable tools: {len(manager.list_tools())}")
    for tool in manager.list_tools():
        print(f"  - {tool.name} ({tool.version})")
    
    # List installed tools
    print(f"\nInstalled tools: {len(manager.list_installed())}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_tool_manager()