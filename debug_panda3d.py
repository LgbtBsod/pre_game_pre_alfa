#!/usr/bin/env python3
"""
Panda3D Diagnostics
"""

import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

try:
    import panda3d
    print(f"✓ panda3d module found: {panda3d.__file__}")
except ImportError as e:
    print(f"✗ panda3d module not found: {e}")

try:
    import direct
    print(f"✓ direct module found: {direct.__file__}")
except ImportError as e:
    print(f"✗ direct module not found: {e}")

try:
    from direct.showbase.ShowBase import ShowBase
    print("✓ ShowBase successfully imported")
except ImportError as e:
    print(f"✗ ShowBase import failed: {e}")

try:
    from panda3d.core import WindowProperties
    print("✓ WindowProperties successfully imported")
except ImportError as e:
    print(f"✗ WindowProperties import failed: {e}")

print("\nChecking pip list:")
import subprocess
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    if "panda3d" in result.stdout.lower():
        print("✓ Panda3D found in pip list")
    else:
        print("✗ Panda3D not found in pip list")
        print("pip list output:")
        print(result.stdout)
except Exception as e:
    print(f"Error running pip list: {e}")
