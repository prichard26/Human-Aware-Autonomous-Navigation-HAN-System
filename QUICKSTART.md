# 🚀 HAAN System - Quick Start Guide

Welcome to the **Human-Aware Autonomous Navigation (HAAN) System**! This guide will get you up and running in just a few minutes.

## ⚡ Quick Setup (5 Minutes)

### 1. **Install Dependencies**
```bash
# Run the automated setup script
python setup.py
```

### 2. **Launch the GUI**
```bash
# Start the interactive GUI simulator
python run_gui.py
```

### 3. **Or Use Command Line**
```bash
# Run the command-line interface
python run_cli.py
```

## 🎮 Using the GUI Simulator

The GUI provides an intuitive interface for running simulations:

1. **📸 Select Image**: Click "Browse" to select an input image
2. **⚙️ Configure Settings**: Adjust simulation parameters
3. **🚀 Start Simulation**: Click "Start Simulation" to begin
4. **📊 View Results**: Watch the real-time visualization
5. **🔄 Restart**: Use "Restart" to run again with new settings

## 🖥️ Using the Command Line

For advanced users and automation:

```python
from enhanced_main import HAANSystem

# Initialize the system
haan = HAANSystem()

# Process an image
result = haan.process_image("path/to/your/image.jpg")

# Run simulation
simulation_result = haan.run_simulation(
    result['obstacles_pos'],
    result['obstacles_dir_speed']
)
```

## 📁 Project Structure

```
HAAN/
├── 🎮 GUI Interface
│   ├── gui_simulator.py      # Main GUI application
│   ├── launch_gui.py         # GUI launcher
│   └── run_gui.py           # Quick GUI start
├── 🤖 Core System
│   ├── enhanced_main.py     # Enhanced main system
│   ├── src/                 # Source code modules
│   └── run_cli.py          # Command line interface
├── 📊 Visualization
│   ├── debug_output/        # Debug images and plots
│   └── results/            # Simulation results
└── 📚 Documentation
    ├── README.md           # Comprehensive documentation
    ├── QUICKSTART.md       # This file
    └── setup.py            # Automated setup
```

## 🔧 Troubleshooting

### Common Issues

**❌ "Module not found" errors**
```bash
# Reinstall dependencies
pip install -r requirements_gui.txt
```

**❌ GUI won't start**
```bash
# Check if tkinter is available
python -c "import tkinter"
```

**❌ Models not loading**
- Ensure `model/orientation_model.pkl` exists
- Check that all dependencies are installed

**❌ Performance issues**
- Close other applications to free up memory
- Reduce simulation parameters (fewer obstacles, shorter time)

### Getting Help

1. **📖 Check the full README.md** for detailed documentation
2. **🐛 Report issues** on GitHub with error messages
3. **💬 Join the community** for support and discussions

## 🎯 Example Workflows

### Basic Human Detection
```python
# Load system
haan = HAANSystem()

# Process image with humans
result = haan.process_image("crowd.jpg")
print(f"Detected {len(result['detections'])} people")
```

### Full Navigation Simulation
```python
# Complete workflow
result = haan.process_image("input.jpg")
simulation = haan.run_simulation(
    result['obstacles_pos'],
    result['obstacles_dir_speed']
)
animation = haan.create_animation(simulation)
```

### Performance Monitoring
```python
# Check system status
status = haan.get_system_status()
print(f"Performance: {status['performance']}")
print(f"Errors: {status['errors']}")
```

## 🚀 Advanced Features

### Custom Configuration
```python
config = {
    'robot_speed': 2.0,
    'simulation_time': 50000,
    'display_results': True
}
haan = HAANSystem(config)
```

### Debug Visualization
```python
# Enable debug output
haan.config['save_debug_images'] = True
haan.config['debug_output_dir'] = 'my_debug_output'
```

### Performance Optimization
```python
# Monitor performance
haan.performance_monitor.start_monitoring()
# ... run simulation ...
haan.save_performance_report("performance.png")
```

## 📈 Next Steps

1. **🎓 Learn More**: Read the full README.md
2. **🔬 Experiment**: Try different images and parameters
3. **🤝 Contribute**: Help improve the system
4. **📚 Study**: Explore the source code in `src/`

---

**🎉 You're all set! Start exploring the amazing world of human-aware robot navigation!**

For more information, check out the [full documentation](README.md) or [report an issue](https://github.com/prichard26/Human-Aware-Autonomous-Navigation-HAN-System/issues).
