#!/usr/bin/env python3
"""
Demo script showing the original HAAN simulation aesthetics.
This demonstrates the proper visualization style and moving obstacles.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

def create_demo_simulation():
    """Create a demo simulation with original aesthetics."""
    print("🎬 Creating demo simulation with original aesthetics...")
    
    # Simulation parameters (matching original)
    SCALE = 0.3
    SIMULATION_TIME = 1000
    DT = 100
    steps = int(SIMULATION_TIME / DT)
    
    # Create demo data
    robot_positions = []
    cost_map_times = []
    dynamic_obstacles_times = []
    dynamic_obstacles_dir_speed_times = []
    path_times = []
    
    # Initialize robot path (simple straight line)
    start = (0, 0)
    goal = (-20 * SCALE, 900 * SCALE)
    
    for t in range(steps):
        # Robot moves towards goal
        progress = t / steps
        robot_x = start[0] + (goal[0] - start[0]) * progress
        robot_y = start[1] + (goal[1] - start[1]) * progress
        robot_positions.append((robot_x, robot_y))
        
        # Create moving obstacles
        num_obstacles = 5
        obstacles = np.zeros((num_obstacles, 2))
        dir_speeds = []
        
        for i in range(num_obstacles):
            # Obstacles move in circular patterns
            angle = (t * 0.1 + i * 2 * np.pi / num_obstacles) % (2 * np.pi)
            radius = 50 + i * 20
            obstacles[i, 0] = radius * np.cos(angle)
            obstacles[i, 1] = 100 + radius * np.sin(angle)
            dir_speeds.append((angle + np.pi/2, 1.0))  # Perpendicular to radius
        
        dynamic_obstacles_times.append(obstacles)
        dynamic_obstacles_dir_speed_times.append(dir_speeds)
        
        # Create cost map (simple circular obstacles)
        cost_map = np.zeros((int(1280*SCALE), int(1000*SCALE)))
        for obs in obstacles:
            x, y = int(obs[0] + 640*SCALE), int(obs[1])
            if 0 <= x < cost_map.shape[0] and 0 <= y < cost_map.shape[1]:
                # Create circular influence
                for dx in range(-30, 31):
                    for dy in range(-30, 31):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < cost_map.shape[0] and 0 <= ny < cost_map.shape[1] and
                            dx*dx + dy*dy <= 900):  # 30 pixel radius
                            distance = np.sqrt(dx*dx + dy*dy)
                            influence = max(0, 1 - distance/30)
                            cost_map[nx, ny] = max(cost_map[nx, ny], influence)
        
        cost_map_times.append(cost_map)
        
        # Simple path (straight line to goal)
        path = [(robot_x, robot_y), goal]
        path_times.append(path)
    
    return {
        'robot_positions': robot_positions,
        'cost_map_times': cost_map_times,
        'dynamic_obstacles_times': dynamic_obstacles_times,
        'dynamic_obstacles_dir_speed_times': dynamic_obstacles_dir_speed_times,
        'path_times': path_times,
        'goal': goal,
        'simulation_time': SIMULATION_TIME,
        'dt': DT
    }

def animate_demo_simulation(simulation_data):
    """Animate the demo simulation with original aesthetics."""
    print("🎨 Creating animation with original aesthetics...")
    
    fig, ax = plt.subplots(figsize=(12.8, 10))
    
    def update(frame):
        ax.clear()
        
        # Display cost map with original hot colormap
        if frame < len(simulation_data['cost_map_times']):
            cost_map = simulation_data['cost_map_times'][frame]
            cost_map_display = cost_map.T
            ax.imshow(cost_map_display, cmap='hot', origin='lower', 
                     extent=[-192, 192, 0, 300], alpha=0.7)
        
        # Plot robot position
        if frame < len(simulation_data['robot_positions']):
            robot_pos = simulation_data['robot_positions'][frame]
            ax.plot(robot_pos[0], robot_pos[1], marker='x', color='green', 
                   markersize=15, mew=3, label='Robot')
        
        # Plot goal position
        goal = simulation_data['goal']
        ax.plot(goal[0], goal[1], marker='x', color='magenta', 
               markersize=15, mew=3, label='Goal')
        
        # Plot moving obstacles with direction arrows
        if (frame < len(simulation_data['dynamic_obstacles_times']) and 
            frame < len(simulation_data['dynamic_obstacles_dir_speed_times'])):
            
            obstacles = simulation_data['dynamic_obstacles_times'][frame]
            dir_speeds = simulation_data['dynamic_obstacles_dir_speed_times'][frame]
            
            for obstacle_pos, (direction, speed) in zip(obstacles, dir_speeds):
                # Plot obstacle position
                ax.scatter(obstacle_pos[0], obstacle_pos[1], c='blue', s=50, marker='o')
                
                # Plot direction arrow
                arrow_length = 20
                dx = np.cos(direction) * arrow_length
                dy = np.sin(direction) * arrow_length
                ax.arrow(obstacle_pos[0], obstacle_pos[1], dx, dy, 
                        head_width=5, head_length=8, fc='blue', ec='blue', alpha=0.8)
        
        # Plot current path
        if (frame < len(simulation_data['path_times']) and 
            simulation_data['path_times'][frame] is not None):
            path = simulation_data['path_times'][frame]
            if len(path) > 1:
                path_x = [pos[0] for pos in path]
                path_y = [pos[1] for pos in path]
                ax.plot(path_x, path_y, color='#ff6961', linestyle='--', 
                       linewidth=2, alpha=0.8, label='Planned Path')
        
        # Plot robot's traveled path
        if frame > 0:
            past_positions = simulation_data['robot_positions'][:frame+1]
            if len(past_positions) > 1:
                past_x = [pos[0] for pos in past_positions]
                past_y = [pos[1] for pos in past_positions]
                ax.plot(past_x, past_y, color='red', linestyle='-', 
                       linewidth=2, alpha=0.6, label='Robot Path')
        
        # Set plot properties (matching original)
        ax.set_title(f'HAAN Demo Simulation - Time Step {frame}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position (cm)')
        ax.set_ylabel('Y Position (cm)')
        ax.set_xlim(-192, 192)
        ax.set_ylim(0, 300)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=len(simulation_data['robot_positions']), 
                        interval=100, repeat=True)
    
    print("✅ Demo animation created!")
    print("🎬 Animation controls:")
    print("   - Close window to stop")
    print("   - Animation will loop automatically")
    
    plt.show()
    return anim

def main():
    """Main demo function."""
    print("🤖 HAAN Demo - Original Aesthetics")
    print("=" * 40)
    
    try:
        # Create demo simulation
        simulation_data = create_demo_simulation()
        print(f"✅ Created simulation with {len(simulation_data['robot_positions'])} time steps")
        
        # Animate the simulation
        anim = animate_demo_simulation(simulation_data)
        
        print("\n🎉 Demo completed!")
        print("💡 This shows the original HAAN simulation aesthetics:")
        print("   - Hot colormap for cost visualization")
        print("   - Moving obstacles with direction arrows")
        print("   - Robot path tracking")
        print("   - Real-time animation")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
