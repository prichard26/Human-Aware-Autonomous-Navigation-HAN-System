"""
navigation_algo.py
Contains functions for path planning and navigation in dynamic environments.
"""

import numpy as np
import heapq
import matplotlib.pyplot as plt

def update_probability_grid(prob_grid, dynamic_obstacles, time_step):
    """
    Updates the probability grid based on dynamic obstacles' positions.

    Args:
    - prob_grid (numpy array): The probability grid.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - time_step (int): The time step for prediction.

    Returns:
    - new_prob_grid (numpy array): The updated probability grid.
    """
    new_prob_grid = np.copy(prob_grid)
    for obs in dynamic_obstacles:
        x, y, dx, dy = obs
        for step in range(1, 6):  # Predict the next 5 steps
            new_x, new_y = x + dx * step, y + dy * step
            if 0 <= new_x < prob_grid.shape[1] and 0 <= new_y < prob_grid.shape[0]:
                new_prob_grid[int(new_y), int(new_x)] = min(1, new_prob_grid[int(new_y), int(new_x)] + 0.5)
    return new_prob_grid

def heuristic(a, b):
    """
    Heuristic function for A* algorithm (Euclidean distance).

    Args:
    - a (tuple): The first point.
    - b (tuple): The second point.

    Returns:
    - distance (float): The Euclidean distance between the points.
    """
    return np.linalg.norm(np.array(a) - np.array(b))

def modified_cost(current, neighbor, prob_grid):
    """
    Calculates the modified cost considering the distance and probability of obstacles.

    Args:
    - current (tuple): The current point.
    - neighbor (tuple): The neighboring point.
    - prob_grid (numpy array): The probability grid.

    Returns:
    - cost (float): The modified cost.
    """
    base_cost = heuristic(current, neighbor)
    prob_cost = prob_grid[neighbor[0], neighbor[1]]
    return base_cost + prob_cost

def probabilistic_astar(grid, prob_grid, start, goal):
    """
    Probabilistic A* algorithm for path planning.

    Args:
    - grid (numpy array): The grid representing the environment.
    - prob_grid (numpy array): The probability grid.
    - start (tuple): The start point.
    - goal (tuple): The goal point.

    Returns:
    - path (list of tuples): The path from start to goal, or None if no path is found.
    """
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    open_heap = []
    heapq.heappush(open_heap, (fscore[start], start))
    
    while open_heap:
        current = heapq.heappop(open_heap)[1]
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < grid.shape[0]:
                if 0 <= neighbor[1] < grid.shape[1]:
                    if grid[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    continue
            else:
                continue
                
            tentative_g_score = gscore[current] + modified_cost(current, neighbor, prob_grid)
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                continue
                
            if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_heap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (fscore[neighbor], neighbor))
                
    return None

def display_path(grid, path, prob_grid, dynamic_obstacles, start, goal):
    """
    Displays the grid, path, and dynamic obstacles.

    Args:
    - grid (numpy array): The grid representing the environment.
    - path (list of tuples): The path from start to goal.
    - prob_grid (numpy array): The probability grid.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - start (tuple): The start point.
    - goal (tuple): The goal point.
    """
    fig, ax = plt.subplots(figsize=(8, 12.8))
    ax.imshow(grid, cmap=plt.cm.binary, origin='lower')
    
    # Display dynamic obstacles
    for obs in dynamic_obstacles:
        x, y, dx, dy = obs
        for step in range(1, 6):  # Predict the next 5 steps
            new_x, new_y = x + dx * step, y + dy * step
            if 0 <= new_x < grid.shape[0] and 0 <= new_y < grid.shape[1]:
                ax.plot(new_x, new_y, marker='x', color='blue', markersize=5)
    
    # Display path
    if path:
        for (i, j) in path:
            ax.plot(i, j, marker='o', color='red', markersize=5)
    
    # Display start and goal positions
    ax.plot(start[0], start[1], marker='o', color='green', markersize=10, label='Start')
    ax.plot(goal[0], goal[1], marker='o', color='magenta', markersize=10, label='Goal')
    
    plt.legend()
    plt.xlim(0, grid.shape[0])
    plt.ylim(0, grid.shape[1])
    plt.xlabel('Horizontal position (scaled)')
    plt.ylabel('Depth (scaled)')
    plt.title('2D Top View with Path and Dynamic Obstacles')
    plt.grid(True)
    plt.show()
