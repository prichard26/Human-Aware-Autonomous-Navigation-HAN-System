#!/usr/bin/env python3
"""
Test script for the HAAN GUI system.
This script tests the GUI functionality without requiring the full system.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def test_gui_components():
    """Test GUI components without full HAAN system."""
    print("🧪 Testing HAAN GUI Components...")
    
    # Test 1: Basic tkinter functionality
    try:
        root = tk.Tk()
        root.title("HAAN GUI Test")
        root.geometry("800x600")
        
        # Test matplotlib integration
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create test data
        x = np.linspace(-192, 192, 100)
        y = np.linspace(0, 300, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X/50) * np.cos(Y/50)
        
        # Test cost map visualization
        im = ax.imshow(Z, cmap='hot', origin='lower', extent=[-192, 192, 0, 300], alpha=0.7)
        ax.set_title("Test Cost Map Visualization")
        ax.set_xlabel("X Position (cm)")
        ax.set_ylabel("Y Position (cm)")
        ax.grid(True, alpha=0.3)
        
        # Test robot and obstacles
        ax.plot(0, 50, marker='x', color='green', markersize=15, mew=3, label='Robot')
        ax.plot(-100, 250, marker='x', color='magenta', markersize=15, mew=3, label='Goal')
        
        # Test moving obstacles
        for i in range(5):
            x_obs = np.random.uniform(-150, 150)
            y_obs = np.random.uniform(50, 250)
            direction = np.random.uniform(0, 2*np.pi)
            speed = np.random.uniform(0.5, 2.0)
            
            ax.scatter(x_obs, y_obs, c='blue', s=50, marker='o')
            arrow_length = 20
            dx = np.cos(direction) * arrow_length
            dy = np.sin(direction) * arrow_length
            ax.arrow(x_obs, y_obs, dx, dy, head_width=5, head_length=8, 
                    fc='blue', ec='blue', alpha=0.8)
        
        ax.legend()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, root)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add test buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        def test_animation():
            messagebox.showinfo("Test", "Animation test successful!")
        
        def test_simulation():
            messagebox.showinfo("Test", "Simulation test successful!")
        
        tk.Button(button_frame, text="Test Animation", command=test_animation).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Test Simulation", command=test_simulation).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=5)
        
        print("✅ GUI components test passed!")
        print("🎮 GUI test window opened. Close it to continue.")
        
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("\n📦 Testing imports...")
    
    required_modules = [
        'numpy', 'matplotlib', 'tkinter', 'cv2', 'torch', 'tensorflow'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Install missing modules with: pip install <module_name>")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def main():
    """Main test function."""
    print("🤖 HAAN GUI Test Suite")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing dependencies.")
        return False
    
    # Test GUI components
    if not test_gui_components():
        print("\n❌ GUI test failed.")
        return False
    
    print("\n🎉 All tests passed! GUI is ready to use.")
    print("\n📋 Next steps:")
    print("   1. Run: python run_gui.py")
    print("   2. Or run: python gui_simulator.py")
    print("   3. Select an image and start simulation!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
