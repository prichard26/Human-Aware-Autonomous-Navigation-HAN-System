#!/usr/bin/env python3
"""
Test script to verify coordinate system and bounds checking.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simulation_a_star import x_to_grid, y_to_grid, grid_to_x, calculate_cost_map, find_a_star_proba
import numpy as np

def test_coordinate_system():
    """Test the coordinate conversion functions."""
    print("🧪 Testing Coordinate System")
    print("=" * 40)
    
    SCALE = 0.3
    
    # Test coordinates
    test_coords = [
        (0, 0),           # Start
        (-60, 270),       # Goal
        (-100, 100),      # Random point
        (100, 200),       # Random point
        (-192, 0),        # Edge case
        (192, 300)        # Edge case
    ]
    
    print("Testing coordinate conversions:")
    for world_x, world_y in test_coords:
        grid_x = x_to_grid(world_x)
        grid_y = y_to_grid(world_y)
        back_x = grid_to_x(grid_x)
        back_y = grid_y  # y conversion is identity
        
        print(f"World: ({world_x:4.0f}, {world_y:4.0f}) -> Grid: ({grid_x:3d}, {grid_y:3d}) -> Back: ({back_x:4.0f}, {back_y:4.0f})")
    
    print("\nTesting bounds:")
    grid_size = (int(1280*SCALE), int(1000*SCALE))
    print(f"Grid size: {grid_size}")
    
    for world_x, world_y in test_coords:
        grid_x = x_to_grid(world_x)
        grid_y = y_to_grid(world_y)
        in_bounds = (0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1])
        print(f"({world_x:4.0f}, {world_y:4.0f}) -> Grid({grid_x:3d}, {grid_y:3d}) -> In bounds: {in_bounds}")

def test_cost_map():
    """Test cost map generation."""
    print("\n🧪 Testing Cost Map Generation")
    print("=" * 40)
    
    # Create test obstacles
    obstacles = np.array([
        [-50, 100],
        [50, 150],
        [0, 200]
    ])
    
    dir_speeds = [
        (0, 1.0),
        (np.pi/2, 1.0),
        (np.pi, 1.0)
    ]
    
    # Generate cost map
    cost_map = calculate_cost_map(obstacles, dir_speeds)
    print(f"Cost map shape: {cost_map.shape}")
    print(f"Cost map bounds: x=[0, {cost_map.shape[0]}], y=[0, {cost_map.shape[1]}]")
    print(f"Max cost: {np.max(cost_map):.3f}")
    print(f"Non-zero cells: {np.count_nonzero(cost_map)}")

def test_pathfinding():
    """Test pathfinding with simple scenario."""
    print("\n🧪 Testing Pathfinding")
    print("=" * 40)
    
    # Create simple cost map
    grid_size = (int(1280*0.3), int(1000*0.3))
    cost_map = np.zeros(grid_size)
    
    # Add some obstacles
    cost_map[100:120, 50:70] = 0.8  # Obstacle
    cost_map[200:220, 150:170] = 0.8  # Obstacle
    
    # Test pathfinding
    start = (0, 0)
    goal = (-60, 270)
    
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Cost map shape: {cost_map.shape}")
    
    # Convert to grid coordinates
    start_grid = (x_to_grid(start[0]), y_to_grid(start[1]))
    goal_grid = (x_to_grid(goal[0]), y_to_grid(goal[1]))
    
    print(f"Start grid: {start_grid}")
    print(f"Goal grid: {goal_grid}")
    
    # Check bounds
    in_bounds_start = (0 <= start_grid[0] < cost_map.shape[0] and 0 <= start_grid[1] < cost_map.shape[1])
    in_bounds_goal = (0 <= goal_grid[0] < cost_map.shape[0] and 0 <= goal_grid[1] < cost_map.shape[1])
    
    print(f"Start in bounds: {in_bounds_start}")
    print(f"Goal in bounds: {in_bounds_goal}")
    
    if in_bounds_start and in_bounds_goal:
        path = find_a_star_proba(cost_map, start, goal)
        if path:
            print(f"✅ Path found with {len(path)} waypoints")
            print(f"First few waypoints: {path[:5]}")
        else:
            print("❌ No path found")
    else:
        print("❌ Start or goal out of bounds")

def main():
    """Main test function."""
    print("🤖 HAAN Coordinate System Test")
    print("=" * 50)
    
    try:
        test_coordinate_system()
        test_cost_map()
        test_pathfinding()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
