"""
Complete backend test
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fwb.core import ToolManager, ProfileManager, DependencyResolver
from fwb.models import Tool

def test_backend():
    print("=" * 60)
    print("  FORENSIC WORKSTATION BUILDER - BACKEND TEST")
    print("=" * 60)
    
    # 1. Test ToolManager
    print("\n📦 Testing ToolManager...")
    manager = ToolManager()
    
    # Load CyberChef
    manifest_path = Path("src/tools/cyberchef.json")
    if manifest_path.exists():
        manager.load_tool(manifest_path)
        print("  ✅ CyberChef loaded")
    else:
        print("  ⚠️ CyberChef manifest not found (expected)")
    
    # Create additional tool manifests
    print("\n📦 Loading additional tools...")
    # We'll add more tools later
    
    print(f"  Total tools: {len(manager.list_tools())}")
    print(f"  Installed: {len(manager.list_installed())}")
    
    # 2. Test ProfileManager
    print("\n📋 Testing ProfileManager...")
    profile_manager = ProfileManager()
    profiles = profile_manager.list_profiles()
    
    if profiles:
        for profile in profiles:
            print(f"  - {profile.name} ({len(profile.tools)} tools)")
    else:
        print("  ⚠️ No profiles loaded (expected for now)")
    
    # 3. Test DependencyResolver
    print("\n🔗 Testing DependencyResolver...")
    resolver = DependencyResolver()
    
    # Build tool map
    tool_map = {}
    for tool in manager.list_tools():
        tool_map[tool.id] = tool
    
    # Add some dependencies for testing
    # Create a sample dependency chain
    class TestTool(Tool):
        pass
    
    # Create mock tools with dependencies
    mock_tools = {}
    
    # Tool A depends on Tool B
    tool_a = Tool(
        id="tool_a",
        name="Tool A",
        description="Test tool A",
        category="Test",
        version="1.0",
        supported_os=["windows"],
        install_method="portable",
        download_url="",
        dependencies=["tool_b"]
    )
    mock_tools["tool_a"] = tool_a
    
    tool_b = Tool(
        id="tool_b",
        name="Tool B",
        description="Test tool B",
        category="Test",
        version="1.0",
        supported_os=["windows"],
        install_method="portable",
        download_url=""
    )
    mock_tools["tool_b"] = tool_b
    
    resolver.set_tools(mock_tools)
    plan = resolver.get_install_plan(["tool_a"])
    
    print(f"  Installation batches: {len(plan['batches'])}")
    for i, batch in enumerate(plan['batches']):
        print(f"    Batch {i+1}: {', '.join(batch)}")
    print(f"  Total tools: {plan['total_tools']}")
    
    print("\n" + "=" * 60)
    print("  ✅ BACKEND TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_backend()