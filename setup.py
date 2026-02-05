"""
Setup script for Free Sitemap Generator.
Builds standalone executable with PyInstaller.
"""

import sys
import subprocess
from pathlib import Path


def build():
    """Build the executable using PyInstaller."""
    print("🗺️  Building Free Sitemap Generator...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=FreeSitemapGenerator",
        "--onefile",
        "--windowed",
        "--icon=NONE",
        "--add-data=sitemap_generator:sitemap_generator",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=aiohttp",
        "--hidden-import=lxml",
        "--collect-all=PyQt6",
        "main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ Build successful!")
        print("📁 Executable location: dist/FreeSitemapGenerator")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()
