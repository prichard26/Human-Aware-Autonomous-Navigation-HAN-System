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
            'num_obstacles': tk.IntVar(value=5),  # Fewer obstacles for testing
            'robot_speed': tk.DoubleVar(value=1.11),
            'simulation_time': tk.IntVar(value=5000),  # Shorter simulation time
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
        ttk.Spinbox(params_frame, from_=1000, to=100000, increment=1000, 
                   textvariable=self.simulation_config['simulation_time'], width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Goal position
        ttk.Label(params_frame, text="Goal X:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.goal_x_var = tk.DoubleVar(value=-20)
        ttk.Spinbox(params_frame, from_=-200, to=200, increment=10, 
                   textvariable=self.goal_x_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(params_frame, text="Goal Y:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.goal_y_var = tk.DoubleVar(value=150)
        ttk.Spinbox(params_frame, from_=0, to=300, increment=10, 
                   textvariable=self.goal_y_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=2)
        
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
        
        # Animation control buttons
        self.pause_button = ttk.Button(button_frame, text="⏸️ Pause", 
                                     command=self.pause_animation, state='disabled')
        self.pause_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.resume_button = ttk.Button(button_frame, text="▶️ Resume", 
                                      command=self.resume_animation, state='disabled')
        self.resume_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.reset_animation_button = ttk.Button(button_frame, text="🔄 Reset Animation", 
                                               command=self.reset_animation, state='disabled')
        self.reset_animation_button.grid(row=1, column=2, padx=5, pady=5)
        
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
        
        # Create matplotlib figure with proper sizing
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Robot Navigation Simulation", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("X Position (cm)")
        self.ax.set_ylabel("Y Position (cm)")
        self.ax.grid(True, alpha=0.3)
        
        # Set proper limits to match original simulation
        self.ax.set_xlim(-192, 192)  # -640*0.3 to 640*0.3
        self.ax.set_ylim(0, 300)     # 0*0.3 to 1000*0.3
        
        # Create canvas with proper sizing
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Initialize animation variables
        self.animation_data = None
        self.current_frame = 0
        self.animation_running = False
        
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
            
            # Update goal position from GUI
            goal_x = self.goal_x_var.get()
            goal_y = self.goal_y_var.get()
            self.haan_system.config['goal'] = (goal_x, goal_y)
            
            # Check if image is provided
            if self.current_image_path.get() and os.path.exists(self.current_image_path.get()):
                self.log("📸 Processing input image...")
                # Process image
                result = self.haan_system.process_image(self.current_image_path.get())
                
                if not result.get('success', False):
                    self.simulation_queue.put(('error', f"Image processing failed: {result.get('error', 'Unknown error')}"))
                    return
                
                self.log("✅ Image processing completed")
                
                # Run simulation with image-based obstacles
                simulation_result = self.haan_system.run_simulation(
                    result['obstacles_pos'],
                    result['obstacles_dir_speed'],
                    use_internal_obstacles=False,
                    num_internal_obstacles=0
                )
            else:
                self.log("🎲 Using randomly generated obstacles...")
                # Run simulation with random obstacles only
                simulation_result = self.haan_system.run_simulation(
                    np.array([]),  # Empty array for image-based obstacles
                    [],  # Empty list for image-based obstacle directions
                    use_internal_obstacles=True,
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
                        # Enable animation controls
                        self.pause_button.config(state='normal')
                        self.resume_button.config(state='disabled')
                        self.reset_animation_button.config(state='normal')
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
        """Display simulation results with original aesthetics and animation."""
        try:
            # Store animation data for playback
            self.animation_data = simulation_result
            self.current_frame = 0
            self.animation_running = True
            
            # Start animation
            self._animate_simulation()
            
        except Exception as e:
            self.log(f"❌ Error displaying results: {e}")
    
    def _animate_simulation(self):
        """Animate the simulation with original cost map visualization."""
        if not self.animation_data or not self.animation_running:
            return
            
        try:
            # Get current frame data
            cost_maps = self.animation_data.get('cost_map_times', [])
            robot_positions = self.animation_data.get('robot_positions', [])
            dynamic_obstacles_times = self.animation_data.get('dynamic_obstacles_times', [])
            dynamic_obstacles_dir_speed_times = self.animation_data.get('dynamic_obstacles_dir_speed_times', [])
            path_times = self.animation_data.get('path_times', [])
            
            if self.current_frame >= len(cost_maps):
                self.current_frame = 0  # Loop animation
            
            # Clear and setup plot
            self.ax.clear()
            
            # Display cost map with original hot colormap
            if self.current_frame < len(cost_maps):
                cost_map = cost_maps[self.current_frame]
                # Transpose and flip to match original orientation
                cost_map_display = cost_map.T
                im = self.ax.imshow(cost_map_display, cmap='hot', origin='lower', 
                                  extent=[-192, 192, 0, 300], alpha=0.7)
            
            # Plot robot position
            if self.current_frame < len(robot_positions):
                robot_pos = robot_positions[self.current_frame]
                self.ax.plot(robot_pos[0], robot_pos[1], marker='x', color='green', 
                           markersize=15, mew=3, label='Robot')
            
            # Plot goal position
            goal = self.haan_system.config['goal']
            self.ax.plot(goal[0], goal[1], marker='x', color='magenta', 
                       markersize=15, mew=3, label='Goal')
            
            # Plot moving obstacles with direction arrows
            if (self.current_frame < len(dynamic_obstacles_times) and 
                self.current_frame < len(dynamic_obstacles_dir_speed_times)):
                
                obstacles = dynamic_obstacles_times[self.current_frame]
                dir_speeds = dynamic_obstacles_dir_speed_times[self.current_frame]
                
                for obstacle_pos, (direction, speed) in zip(obstacles, dir_speeds):
                    # Plot obstacle position
                    self.ax.scatter(obstacle_pos[0], obstacle_pos[1], c='blue', s=50, marker='o')
                    
                    # Plot direction arrow
                    arrow_length = 20
                    dx = np.cos(direction) * arrow_length
                    dy = np.sin(direction) * arrow_length
                    self.ax.arrow(obstacle_pos[0], obstacle_pos[1], dx, dy, 
                                head_width=5, head_length=8, fc='blue', ec='blue', alpha=0.8)
            
            # Plot current path (convert from grid coordinates to world coordinates)
            if (self.current_frame < len(path_times) and 
                path_times[self.current_frame] is not None):
                path = path_times[self.current_frame]
                if len(path) > 1:
                    # Convert grid coordinates back to world coordinates
                    path_x = [self._grid_to_x(pos[0]) for pos in path]
                    path_y = [pos[1] for pos in path]  # y is already in world coordinates
                    self.ax.plot(path_x, path_y, color='#ff6961', linestyle='--', 
                               linewidth=2, alpha=0.8, label='Planned Path')
            
            # Plot robot's traveled path
            if self.current_frame > 0:
                past_positions = robot_positions[:self.current_frame+1]
                if len(past_positions) > 1:
                    past_x = [pos[0] for pos in past_positions]
                    past_y = [pos[1] for pos in past_positions]
                    self.ax.plot(past_x, past_y, color='red', linestyle='-', 
                               linewidth=2, alpha=0.6, label='Robot Path')
            
            # Set plot properties
            self.ax.set_title(f'HAAN Simulation - Time Step {self.current_frame}', 
                            fontsize=12, fontweight='bold')
            self.ax.set_xlabel('X Position (cm)')
            self.ax.set_ylabel('Y Position (cm)')
            self.ax.set_xlim(-192, 192)
            self.ax.set_ylim(0, 300)
            self.ax.grid(True, alpha=0.3)
            
            # Add legend
            self.ax.legend(loc='upper right', fontsize=8)
            
            # Update canvas
            self.canvas.draw()
            
            # Schedule next frame
            if self.animation_running:
                self.current_frame += 1
                self.root.after(100, self._animate_simulation)  # 10 FPS animation
            
        except Exception as e:
            self.log(f"❌ Animation error: {e}")
            self.animation_running = False
    
    def stop_simulation(self):
        """Stop the current simulation."""
        if not self.is_simulation_running:
            return
        
        self.is_simulation_running = False
        self.animation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.restart_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.resume_button.config(state='disabled')
        self.reset_animation_button.config(state='disabled')
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
    
    def pause_animation(self):
        """Pause the animation."""
        self.animation_running = False
        self.pause_button.config(state='disabled')
        self.resume_button.config(state='normal')
        self.log("⏸️ Animation paused")
    
    def resume_animation(self):
        """Resume the animation."""
        if self.animation_data:
            self.animation_running = True
            self.pause_button.config(state='normal')
            self.resume_button.config(state='disabled')
            self._animate_simulation()
            self.log("▶️ Animation resumed")
    
    def reset_animation(self):
        """Reset animation to beginning."""
        self.current_frame = 0
        self.animation_running = False
        self.pause_button.config(state='disabled')
        self.resume_button.config(state='normal')
        if self.animation_data:
            self._animate_simulation()
        self.log("🔄 Animation reset to beginning")
    
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
