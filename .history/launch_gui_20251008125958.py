#!/usr/bin/env python3
"""
HAAN System GUI Launcher
Simple launcher script for the GUI simulator.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'numpy', 'opencv-python', 'matplotlib', 'scipy', 'pillow',
        'torch', 'tensorflow', 'transformers', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🤖 HAAN System GUI Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("src") or not os.path.exists("gui_simulator.py"):
        print("❌ Please run this script from the HAAN project root directory")
        return
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return
    
    print("✅ All dependencies found!")
    
    # Launch GUI
    print("🚀 Launching HAAN GUI...")
    try:
        import gui_simulator
        gui_simulator.main()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("💡 Try running: python gui_simulator.py")

if __name__ == "__main__":
    main()
