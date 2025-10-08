#!/usr/bin/env python3
"""
GUI Simulator for HAAN System
A simple and intuitive GUI for controlling robot navigation simulations.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import queue

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_main import HAANSystem

class HAANGUI:
    """Main GUI class for the HAAN system simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 HAAN System - Robot Navigation Simulator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize HAAN system
        self.haan_system = None
        self.simulation_thread = None
        self.is_simulation_running = False
        self.simulation_queue = queue.Queue()
        
        # Variables
        self.current_image_path = tk.StringVar()
        self.simulation_config = {
            'use_internal_obstacles': tk.BooleanVar(value=True),
            'num_obstacles': tk.IntVar(value=20),
            'robot_speed': tk.DoubleVar(value=1.11),
            'simulation_time': tk.IntVar(value=100000),
            'dt': tk.IntVar(value=100)
        }
        
        self.setup_ui()
        self.setup_haan_system()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 HAAN System - Robot Navigation Simulator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Controls
        self.setup_control_panel(main_frame)
        
        # Right panel - Visualization
        self.setup_visualization_panel(main_frame)
        
        # Bottom panel - Status and Log
        self.setup_status_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control panel."""
        control_frame = ttk.LabelFrame(parent, text="🎮 Simulation Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Image selection
        ttk.Label(control_frame, text="📸 Input Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        image_frame = ttk.Frame(control_frame)
        image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(image_frame, textvariable=self.current_image_path, width=40).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(image_frame, text="Browse", command=self.browse_image).grid(row=0, column=1)
        
        # Simulation parameters
        params_frame = ttk.LabelFrame(control_frame, text="⚙️ Simulation Parameters", padding="5")
        params_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Use internal obstacles
        ttk.Checkbutton(params_frame, text="Use Internal Obstacles", 
                       variable=self.simulation_config['use_internal_obstacles']).grid(row=0, column=0, sticky=tk.W)
        
        # Number of obstacles
        ttk.Label(params_frame, text="Number of Obstacles:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(params_frame, from_=1, to=50, textvariable=self.simulation_config['num_obstacles'], 
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Robot speed
        ttk.Label(params_frame, text="Robot Speed:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(params_frame, from_=0.1, to=5.0, increment=0.1, 
                   textvariable=self.simulation_config['robot_speed'], width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Simulation time
        ttk.Label(params_frame, text="Simulation Time (ms):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(params_frame, from_=1000, to=1000000, increment=1000, 
                   textvariable=self.simulation_config['simulation_time'], width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Simulation", 
                                     command=self.start_simulation, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop Simulation", 
                                    command=self.stop_simulation, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.restart_button = ttk.Button(button_frame, text="🔄 Restart", 
                                       command=self.restart_simulation, state='disabled')
        self.restart_button.grid(row=0, column=2, padx=5)
        
        # Status indicators
        status_frame = ttk.LabelFrame(control_frame, text="📊 System Status", padding="5")
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
    def setup_visualization_panel(self, parent):
        """Setup the visualization panel."""
        viz_frame = ttk.LabelFrame(parent, text="📊 Simulation Visualization", padding="10")
        viz_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Robot Navigation Simulation")
        self.ax.set_xlabel("X Position")
        self.ax.set_ylabel("Y Position")
        self.ax.grid(True, alpha=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
    def setup_status_panel(self, parent):
        """Setup the status and log panel."""
        status_frame = ttk.LabelFrame(parent, text="📝 System Log", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
    def setup_haan_system(self):
        """Initialize the HAAN system."""
        try:
            self.log("Initializing HAAN system...")
            self.haan_system = HAANSystem()
            self.log("✅ HAAN system initialized successfully!")
            self.update_status("Ready", "green")
        except Exception as e:
            self.log(f"❌ Error initializing HAAN system: {e}")
            self.update_status("Error", "red")
    
    def browse_image(self):
        """Browse for input image."""
        file_path = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.current_image_path.set(file_path)
            self.log(f"Selected image: {file_path}")
    
    def start_simulation(self):
        """Start the simulation in a separate thread."""
        if self.is_simulation_running:
            return
        
        if not self.current_image_path.get():
            messagebox.showerror("Error", "Please select an input image first!")
            return
        
        if not os.path.exists(self.current_image_path.get()):
            messagebox.showerror("Error", "Selected image file does not exist!")
            return
        
        # Update UI state
        self.is_simulation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.restart_button.config(state='disabled')
        self.progress_bar.start()
        self.update_status("Running Simulation...", "blue")
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._run_simulation_thread)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_simulation)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _run_simulation_thread(self):
        """Run simulation in a separate thread."""
        try:
            self.log("🚀 Starting simulation...")
            
            # Process image
            result = self.haan_system.process_image(self.current_image_path.get())
            
            if not result.get('success', False):
                self.simulation_queue.put(('error', f"Image processing failed: {result.get('error', 'Unknown error')}"))
                return
            
            self.log("✅ Image processing completed")
            
            # Run simulation
            simulation_result = self.haan_system.run_simulation(
                result['obstacles_pos'],
                result['obstacles_dir_speed'],
                use_internal_obstacles=self.simulation_config['use_internal_obstacles'].get(),
                num_internal_obstacles=self.simulation_config['num_obstacles'].get()
            )
            
            if simulation_result.get('success', False):
                self.simulation_queue.put(('success', simulation_result))
                self.log("✅ Simulation completed successfully!")
            else:
                self.simulation_queue.put(('error', f"Simulation failed: {simulation_result.get('error', 'Unknown error')}"))
                
        except Exception as e:
            self.simulation_queue.put(('error', f"Unexpected error: {e}"))
            self.log(f"❌ Simulation error: {e}")
    
    def _monitor_simulation(self):
        """Monitor simulation progress and update UI."""
        while self.is_simulation_running:
            try:
                # Check for simulation results
                if not self.simulation_queue.empty():
                    result_type, data = self.simulation_queue.get_nowait()
                    
                    if result_type == 'success':
                        self._display_simulation_results(data)
                        self.log("🎉 Simulation completed successfully!")
                    elif result_type == 'error':
                        self.log(f"❌ {data}")
                        self.update_status("Error", "red")
                
                time.sleep(0.1)  # Check every 100ms
                
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                self.log(f"❌ Monitoring error: {e}")
                break
    
    def _display_simulation_results(self, simulation_result):
        """Display simulation results on the plot."""
        try:
            self.ax.clear()
            
            # Plot robot path
            if simulation_result.get('robot_positions'):
                robot_positions = simulation_result['robot_positions']
                robot_x = [pos[0] for pos in robot_positions]
                robot_y = [pos[1] for pos in robot_positions]
                self.ax.plot(robot_x, robot_y, 'g-', linewidth=2, label='Robot Path')
                self.ax.scatter(robot_x[0], robot_y[0], c='green', s=100, marker='o', label='Start')
                self.ax.scatter(robot_x[-1], robot_y[-1], c='red', s=100, marker='x', label='End')
            
            # Plot obstacles
            if simulation_result.get('dynamic_obstacles_times'):
                obstacles = simulation_result['dynamic_obstacles_times'][-1]  # Last time step
                if len(obstacles) > 0:
                    obstacle_x = obstacles[:, 0]
                    obstacle_y = obstacles[:, 1]
                    self.ax.scatter(obstacle_x, obstacle_y, c='blue', s=50, marker='s', label='Obstacles')
            
            self.ax.set_title("Robot Navigation Simulation Results")
            self.ax.set_xlabel("X Position")
            self.ax.set_ylabel("Y Position")
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            self.canvas.draw()
            
        except Exception as e:
            self.log(f"❌ Error displaying results: {e}")
    
    def stop_simulation(self):
        """Stop the current simulation."""
        if not self.is_simulation_running:
            return
        
        self.is_simulation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.restart_button.config(state='normal')
        self.progress_bar.stop()
        self.update_status("Stopped", "orange")
        self.log("⏹️ Simulation stopped by user")
    
    def restart_simulation(self):
        """Restart the simulation."""
        self.stop_simulation()
        time.sleep(0.5)  # Brief pause
        self.start_simulation()
    
    def update_status(self, text, color="black"):
        """Update the status label."""
        self.status_label.config(text=text, foreground=color)
    
    def log(self, message):
        """Add a message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_closing(self):
        """Handle application closing."""
        if self.is_simulation_running:
            self.stop_simulation()
        self.root.destroy()

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = HAANGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
