#!/usr/bin/env python3
"""
Fix encoding issues in app.py
"""

import os
import sys

def fix_encoding():
    """Fix UTF-8 encoding issues in app.py"""
    try:
        # Read the file with error handling
        with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Write back with proper UTF-8 encoding
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed encoding issues in app.py")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing encoding: {e}")
        return False

if __name__ == "__main__":
    if fix_encoding():
        print("🚀 Ready to restart application")
    else:
        print("❌ Fix failed")
        sys.exit(1)