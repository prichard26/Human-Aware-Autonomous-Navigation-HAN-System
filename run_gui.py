#!/usr/bin/env python3
"""
HAAN GUI Launcher
Launches the GUI simulator with error handling.
"""

import sys
import os
import traceback

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import tkinter
        import numpy
        import matplotlib
        import cv2
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install missing dependencies with: pip install -r requirements_gui.txt")
        return False

def main():
    """Main launcher function."""
    print("🤖 HAAN GUI Launcher")
    print("=" * 30)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies not met. Please install required packages.")
        return False
    
    try:
        # Add current directory to path
        sys.path.append(os.path.dirname(__file__))
        
        # Import and run GUI
        from gui_simulator import main as gui_main
        print("✅ Starting HAAN GUI...")
        gui_main()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the HAAN project directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Troubleshooting:")
        print("   1. Run: python setup.py")
        print("   2. Check: python test_gui.py")
        print("   3. Ensure all dependencies are installed")
    sys.exit(0 if success else 1)
