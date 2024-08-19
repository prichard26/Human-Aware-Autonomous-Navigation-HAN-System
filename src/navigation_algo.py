import numpy as np
import heapq
import matplotlib.pyplot as plt

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
    prob_cost = prob_grid[neighbor[1], neighbor[0]]
    return base_cost + 5 * prob_cost

def probabilistic_astar(cost_map, start, goal, time_step):
    """
    Probabilistic A* algorithm for path planning.

    Args:
    - cost_map (numpy array): The 3D cost map array.
    - start (tuple): The start point.
    - goal (tuple): The goal point.
    - time_step (int): The specific time step to use in the cost map.

    Returns:
    - path (list of tuples): The path from start to goal, or None if no path is found.
    """
    grid = np.zeros(cost_map[:, :, 0].shape)
    prob_grid = cost_map[:, :, time_step]
    
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]  # 8 directions
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
            if 0 <= neighbor[0] < grid.shape[1]:
                if 0 <= neighbor[1] < grid.shape[0]:
                    if grid[neighbor[1]][neighbor[0]] == 1:
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

def update_robot_position(path, robot_speed, dt):
    """
    Updates the robot's position based on its speed.

    Args:
    - path (list of tuples): The path from the A* algorithm.
    - robot_speed (float): The speed of the robot in centimeters per second.
    - dt (int): The time increment in milliseconds.

    Returns:
    - new_position (tuple): The new position of the robot.
    - remaining_path (list of tuples): The remaining path after the robot moves.
    """
    steps_to_move = int(robot_speed * dt)  # Convert speed to steps based on dt
    if steps_to_move >= len(path):
        return path[-1], []
    else:
        return path[steps_to_move], path[steps_to_move:]

def simulate_robot_navigation(cost_map, start, goal, robot_speed, time_steps=100, dt=10):
    """
    Simulates the robot's navigation using A* algorithm with periodic updates.

    Args:
    - cost_map (numpy array): The 3D cost map array.
    - start (tuple): The start point.
    - goal (tuple): The goal point.
    - robot_speed (float): The speed of the robot in centimeters per second.
    - time_steps (int): The number of time steps to simulate.
    - dt (int): The time increment in milliseconds.

    Returns:
    - path (list of tuples): The final path taken by the robot.
    """
    current_position = start
    final_path = []

    for t in range(0, time_steps):
        path = probabilistic_astar(cost_map, current_position, goal, t)
        if path is None:
            print("No path found!")
            break

        current_position, remaining_path = update_robot_position(path, robot_speed, dt)
        final_path.extend(remaining_path)
        
        if current_position == goal:
            print("Goal reached!")
            break
    
    return final_path

def display_simulation(final_path, cost_map, goal):
    """
    Displays the final path taken by the robot.

    Args:
    - final_path (list of tuples): The final path taken by the robot.
    - cost_map (numpy array): The 3D cost map array.
    - goal (tuple): The goal point.
    """
    plt.figure(figsize=(12.8, 10))
    plt.imshow(cost_map[:, :, 0].T, cmap='hot', origin='lower', extent=[-640, 640, 0, 1000])
    
    for point in final_path:
        plt.plot(point[0], point[1], marker='o', color='green', markersize=5)
    
    plt.plot(goal[0], goal[1], marker='x', color='magenta', markersize=15, mew=3)
    plt.title('Final Path Taken by the Robot')
    plt.xlabel('Horizontal Position (cm)')
    plt.ylabel('Depth (cm)')
    plt.grid(False)
    plt.xlim([-640, 640])
    plt.ylim([0, 1000])
    plt.show()