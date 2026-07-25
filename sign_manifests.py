#!/usr/bin/env python3
"""
Sign all tool manifests with SHA-256 signatures.
Run this after adding/modifying any tool manifest.
"""

import json
from pathlib import Path
import hashlib


def generate_signature(manifest_data):
    """Generate SHA-256 signature from manifest content"""
    data_copy = {k: v for k, v in manifest_data.items() if k != "signature"}
    sorted_data = {k: data_copy[k] for k in sorted(data_copy.keys())}
    json_string = json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_string.encode()).hexdigest()


def sign_manifest(file_path):
    """Sign a single manifest file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        data["signature"] = generate_signature(data)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Signed: {file_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to sign {file_path.name}: {e}")
        return False


def main():
    tools_dir = Path("data/tools")
    
    if not tools_dir.exists():
        print(f"❌ Tools directory not found: {tools_dir}")
        return
    
    manifest_files = list(tools_dir.glob("*.json"))
    
    if not manifest_files:
        print("❌ No manifest files found.")
        return
    
    print(f"🔑 Signing {len(manifest_files)} tool manifests...\n")
    
    signed = 0
    for file_path in manifest_files:
        if sign_manifest(file_path):
            signed += 1
    
    print(f"\n✅ Signed {signed}/{len(manifest_files)} manifests successfully.")


if __name__ == "__main__":
    main()