#!/usr/bin/env python3
"""
Debug script to understand why simulation only runs 2 steps.
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_coordinate_system():
    """Debug the coordinate system."""
    print("🔍 Debugging Coordinate System")
    print("=" * 40)
    
    SCALE = 0.3
    
    # Test coordinates
    start = (0, 0)
    goal = (-20, 200)
    
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    
    # Manual coordinate conversion
    def x_to_grid_manual(x):
        return int(x + int(640*SCALE))
    
    def y_to_grid_manual(y):
        return int(y)
    
    start_grid = (x_to_grid_manual(start[0]), y_to_grid_manual(start[1]))
    goal_grid = (x_to_grid_manual(goal[0]), y_to_grid_manual(goal[1]))
    
    print(f"Start grid: {start_grid}")
    print(f"Goal grid: {goal_grid}")
    
    # Grid size
    grid_size = (int(1280*SCALE), int(1000*SCALE))
    print(f"Grid size: {grid_size}")
    
    # Check bounds
    start_in_bounds = (0 <= start_grid[0] < grid_size[0] and 0 <= start_grid[1] < grid_size[1])
    goal_in_bounds = (0 <= goal_grid[0] < grid_size[0] and 0 <= goal_grid[1] < grid_size[1])
    
    print(f"Start in bounds: {start_in_bounds}")
    print(f"Goal in bounds: {goal_in_bounds}")
    
    if not start_in_bounds:
        print(f"❌ Start out of bounds: {start_grid} not in [0, {grid_size[0]}) x [0, {grid_size[1]})")
    if not goal_in_bounds:
        print(f"❌ Goal out of bounds: {goal_grid} not in [0, {grid_size[0]}) x [0, {grid_size[1]})")

def debug_simple_simulation():
    """Debug a simple simulation scenario."""
    print("\n🔍 Debugging Simple Simulation")
    print("=" * 40)
    
    # Create a simple scenario
    SCALE = 0.3
    grid_size = (int(1280*SCALE), int(1000*SCALE))
    
    print(f"Grid size: {grid_size}")
    
    # Create empty cost map
    cost_map = np.zeros(grid_size)
    print(f"Cost map shape: {cost_map.shape}")
    print(f"Cost map bounds: x=[0, {cost_map.shape[0]}], y=[0, {cost_map.shape[1]}]")
    
    # Test coordinates
    start = (0, 0)
    goal = (-20, 200)
    
    # Convert to grid
    start_grid = (int(start[0] + 640*SCALE), int(start[1]))
    goal_grid = (int(goal[0] + 640*SCALE), int(goal[1]))
    
    print(f"Start: {start} -> Grid: {start_grid}")
    print(f"Goal: {goal} -> Grid: {goal_grid}")
    
    # Check if coordinates are valid
    start_valid = (0 <= start_grid[0] < grid_size[0] and 0 <= start_grid[1] < grid_size[1])
    goal_valid = (0 <= goal_grid[0] < grid_size[0] and 0 <= goal_grid[1] < grid_size[1])
    
    print(f"Start valid: {start_valid}")
    print(f"Goal valid: {goal_valid}")
    
    if start_valid and goal_valid:
        print("✅ Coordinates are valid for pathfinding")
        
        # Simple distance calculation
        distance = np.sqrt((goal_grid[0] - start_grid[0])**2 + (goal_grid[1] - start_grid[1])**2)
        print(f"Distance: {distance:.2f} grid units")
        
        if distance < 10:
            print("⚠️ Goal is very close to start")
        elif distance > 100:
            print("⚠️ Goal is very far from start")
        else:
            print("✅ Distance seems reasonable")
    else:
        print("❌ Invalid coordinates - cannot run pathfinding")

def debug_obstacle_creation():
    """Debug obstacle creation."""
    print("\n🔍 Debugging Obstacle Creation")
    print("=" * 40)
    
    # Create test obstacles
    obstacles = np.array([
        [-50, 100],
        [50, 150],
        [0, 200]
    ])
    
    print(f"Obstacles: {obstacles}")
    
    # Check if obstacles are in bounds
    SCALE = 0.3
    grid_size = (int(1280*SCALE), int(1000*SCALE))
    
    for i, obs in enumerate(obstacles):
        x, y = obs
        grid_x = int(x + 640*SCALE)
        grid_y = int(y)
        in_bounds = (0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1])
        print(f"Obstacle {i}: ({x}, {y}) -> Grid({grid_x}, {grid_y}) -> In bounds: {in_bounds}")

def main():
    """Main debug function."""
    print("🐛 HAAN Simulation Debug")
    print("=" * 50)
    
    try:
        debug_coordinate_system()
        debug_simple_simulation()
        debug_obstacle_creation()
        
        print("\n💡 Recommendations:")
        print("1. Use goal coordinates within bounds: x=[-192, 192], y=[0, 300]")
        print("2. Start with simple scenarios (few obstacles)")
        print("3. Use shorter simulation times for testing")
        print("4. Check that all coordinates convert properly to grid space")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
