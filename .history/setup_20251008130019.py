#!/usr/bin/env python3
"""
HAAN System Setup Script
Comprehensive setup and installation script for the HAAN system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the HAAN system banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🤖 HAAN System - Human-Aware Autonomous Navigation        ║
    ║                                                              ║
    ║    Advanced Robot Navigation with AI-Powered Human          ║
    ║    Detection and Predictive Path Planning                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_system_requirements():
    """Check system requirements."""
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check available memory
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 4:
            print(f"⚠️  Warning: Low memory detected ({memory_gb:.1f} GB)")
            print("   HAAN system requires at least 4GB RAM for optimal performance")
        else:
            print(f"✅ Available memory: {memory_gb:.1f} GB")
    except ImportError:
        print("⚠️  psutil not available, cannot check memory")
    
    # Check disk space
    try:
        disk_usage = os.statvfs('.')
        free_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
        if free_gb < 2:
            print(f"⚠️  Warning: Low disk space ({free_gb:.1f} GB free)")
        else:
            print(f"✅ Available disk space: {free_gb:.1f} GB")
    except:
        print("⚠️  Cannot check disk space")
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Core requirements
    requirements = [
        "numpy>=1.21.0",
        "opencv-python>=4.5.0", 
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "pillow>=8.3.0",
        "torch>=2.0.1",
        "torchvision>=0.15.2",
        "tensorflow>=2.8.0",
        "tensorflow-hub>=0.12.0",
        "transformers>=4.20.0",
        "joblib>=1.1.0",
        "psutil>=5.8.0",
        "tqdm>=4.64.0"
    ]
    
    try:
        for req in requirements:
            print(f"   Installing {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "debug_output",
        "logs", 
        "results",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}/")

def download_models():
    """Download required models."""
    print("\n🤖 Downloading AI models...")
    
    try:
        # This would typically download pre-trained models
        # For now, we'll just create placeholder files
        model_dir = Path("model")
        model_dir.mkdir(exist_ok=True)
        
        # Create a placeholder for the orientation model
        orientation_model = model_dir / "orientation_model.pkl"
        if not orientation_model.exists():
            print("   ⚠️  Orientation model not found. Please ensure model/orientation_model.pkl exists")
        
        print("✅ Model directory structure created")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up models: {e}")
        return False

def test_installation():
    """Test the installation."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test basic imports
        import numpy as np
        import cv2
        import matplotlib.pyplot as plt
        import torch
        import tensorflow as tf
        print("✅ Core libraries imported successfully")
        
        # Test HAAN system import
        sys.path.append('src')
        from enhanced_main import HAANSystem
        print("✅ HAAN system imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def create_launcher_scripts():
    """Create convenient launcher scripts."""
    print("\n🚀 Creating launcher scripts...")
    
    # Create GUI launcher
    gui_launcher = """#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))
from gui_simulator import main
if __name__ == "__main__":
    main()
"""
    
    with open("run_gui.py", "w") as f:
        f.write(gui_launcher)
    
    # Create command line launcher
    cli_launcher = """#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))
from enhanced_main import main
if __name__ == "__main__":
    main()
"""
    
    with open("run_cli.py", "w") as f:
        f.write(cli_launcher)
    
    # Make scripts executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("run_gui.py", 0o755)
        os.chmod("run_cli.py", 0o755)
    
    print("✅ Launcher scripts created:")
    print("   - run_gui.py (GUI interface)")
    print("   - run_cli.py (Command line interface)")

def main():
    """Main setup function."""
    print_banner()
    
    print("🚀 Starting HAAN System Setup...")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please address the issues above.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please check the error messages above.")
        return False
    
    # Create directories
    create_directories()
    
    # Download models
    if not download_models():
        print("\n⚠️  Model setup had issues. Please ensure models are available.")
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please check the error messages above.")
        return False
    
    # Create launcher scripts
    create_launcher_scripts()
    
    print("\n" + "=" * 60)
    print("🎉 HAAN System Setup Complete!")
    print("\n📋 Next Steps:")
    print("   1. Run the GUI: python run_gui.py")
    print("   2. Run CLI: python run_cli.py")
    print("   3. Check the README.md for detailed usage instructions")
    print("\n💡 For support, check the documentation or create an issue on GitHub")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
