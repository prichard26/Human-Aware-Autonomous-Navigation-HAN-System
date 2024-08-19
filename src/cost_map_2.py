import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import heapq

# Heuristic function for A* pathfinding
def heuristic(a, b, weight=1.5):
    """
    Calculate the Euclidean distance between two points a and b,
    with an optional weight to make the heuristic more aggressive.
    
    Args:
    - a (tuple): Coordinates of the first point.
    - b (tuple): Coordinates of the second point.
    - weight (float): Weight to adjust heuristic aggressiveness.
    
    Returns:
    - float: Weighted Euclidean distance between the two points.
    """
    return weight * np.linalg.norm(np.array(a) - np.array(b))

# Cost function that considers the obstacle probability
def modified_cost(current, neighbor, prob_grid):
    """
    Calculate the cost of moving from the current position to a neighbor position,
    considering both the base movement cost and the probability of an obstacle.
    
    Args:
    - current (tuple): Current position in the grid.
    - neighbor (tuple): Neighboring position to evaluate.
    - prob_grid (numpy array): 2D array representing the probability of obstacles in the grid.
    
    Returns:
    - float: Combined cost of moving to the neighbor position.
    """
    base_cost = heuristic(current, neighbor)
    prob_cost = prob_grid[neighbor[0], neighbor[1]]
    return base_cost + 50 * prob_cost

def calculate_cost_map(dynamic_obstacles_pos, grid_size=(1280, 1000)):
    """
    Generate a cost map based on the positions of dynamic obstacles at a certain time.
    
    Args:
    - dynamic_obstacles_pos (numpy array): Array containing the positions of dynamic obstacles.
    - grid_size (tuple): Size of the grid (width, height).
    
    Returns:
    - numpy array: 2D array representing the current cost map.
    """
    cost_map = np.zeros(grid_size)

    def x_to_grid(x):
        return int(x + 640)  # Convert x from [-640, 640] to [0, 1280]

    def y_to_grid(y):
        return int(y)  # y already in [0, 1000]
    
    # Extract grid positions of all obstacles
    grid_coords = np.array([[x_to_grid(obst[0]), y_to_grid(obst[1])] for obst in dynamic_obstacles_pos])

    # Ensure all obstacle positions are within the grid boundaries
    grid_coords = np.clip(grid_coords, [0, 0], [grid_size[0] - 1, grid_size[1] - 1])

    # Influence radius
    radius = 50

    # Create a grid of x and y coordinates
    x_indices, y_indices = np.meshgrid(np.arange(grid_size[0]), np.arange(grid_size[1]), indexing='ij')

    for grid_x, grid_y in grid_coords:
        # Calculate the distance from each point in the grid to the obstacle
        distance_to_center = np.sqrt((x_indices - grid_x) ** 2 + (y_indices - grid_y) ** 2)

        # Apply influence only within the radius
        influence = np.where(distance_to_center <= radius, 1 - (distance_to_center / radius), 0)

        # Update the cost map
        cost_map = np.maximum(cost_map, influence)

    return cost_map


def update_dynamic_obstacles(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, dt, grid_size=(1280, 1000)):
    """
    Update the positions of dynamic obstacles based on their direction and speed, 
    with checks to ensure they stay within the grid boundaries.

    Args:
    - dynamic_obstacles_pos (numpy array): Initial positions of obstacles (num_obstacles, 2).
    - dynamic_obstalcles_dir_speed (list of tuples): List containing the direction and speed of each obstacle.
    - dt (float): Time step for the update.
    - grid_size (tuple): Size of the grid (width, height).

    Returns:
    - numpy array: A 2D array with updated positions of all obstacles (num_obstacles, 2).
    """
    num_obstacles = dynamic_obstacles_pos.shape[0]
    updated_dynamic_obstacles = []

    for i in range(num_obstacles):
        direction, speed = dynamic_obstalcles_dir_speed[i]
        # Calculate the new positions for each obstacle
        futur_x = dynamic_obstacles_pos[i, 0] + np.cos(direction) * speed * dt / 10
        futur_y = dynamic_obstacles_pos[i, 1] + np.sin(direction) * speed * dt / 10

        # LATER Check if the obstacle is within the grid boundaries BUT CHANGE ALLL THE ARRAY
        updated_dynamic_obstacles.append([futur_x, futur_y])

    return np.array(updated_dynamic_obstacles)

# A* pathfinding algorithm
def find_a_star_proba(cost_map, start, goal, max_iterations=1000000000):
    """
    Find the optimal path from start to goal using a probabilistic A* algorithm.
    
    Args:
    - cost_map (numpy array): 2D array representing the cost map.
    - start (tuple): Start position of the robot.
    - goal (tuple): Goal position for the robot.
    - max_iterations (int): Maximum number of iterations to run the algorithm.
    
    Returns:
    - list: List of tuples representing the path from start to goal.
    """
    prob_grid = cost_map
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    open_heap = []
    heapq.heappush(open_heap, (fscore[start], start))
    
    iterations = 0
    
    while open_heap:
        iterations += 1
        if iterations > max_iterations:
            print("Reached maximum iterations, aborting...")
            return None
        
        current = heapq.heappop(open_heap)[1]
        
        if np.linalg.norm(np.array(current) - np.array(goal)) <= 1:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < prob_grid.shape[0] and 0 <= neighbor[1] < prob_grid.shape[1]:
                tentative_g_score = gscore[current] + modified_cost(current, neighbor, prob_grid)
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                    continue
                    
                if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_heap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (fscore[neighbor], neighbor))
    
    print('final nb of iteration :', iterations)

    return None

def simulation(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, start, goal, robot_speed, time_steps=100, dt=10):
    """
    Simulate the robot's movement while avoiding dynamic obstacles.

    Args:
    - dynamic_obstacles_pos (numpy array): Initial positions of obstacles (num_obstacles, 2).
    - dynamic_obstalcles_dir_speed (list of tuples): List containing the direction and speed of each obstacle.
    - start (tuple): Starting position of the robot (x, y).
    - goal (tuple): Goal position (x, y).
    - robot_speed (float): Speed of the robot.
    - time_steps (int): Number of time steps for the simulation.
    - dt (int): Time increment between steps in milliseconds.

    Returns:
    - tuple: Containing robot positions over time, cost maps over time, obstacle positions over time, and the path.
    """
    robot_positions = [start]
    cost_map_times = []
    path_times = []
    dynamic_obstacles_times = [dynamic_obstacles_pos]  # Start with initial obstacle positions
    steps = int(time_steps / dt)
    goal_reached = False
    
    # Calculate and store the initial cost map (at time step 0)
    initial_cost_map = calculate_cost_map(dynamic_obstacles_pos)
    cost_map_times.append(initial_cost_map)

    for t in range(steps):
        if goal_reached:
            print(f"Goal reached at step {t}.")
            break

        # Update obstacle positions
        current_dynamic_obstacles_pos = update_dynamic_obstacles(dynamic_obstacles_times[-1], dynamic_obstalcles_dir_speed, dt)
        dynamic_obstacles_times.append(current_dynamic_obstacles_pos)

        # Calculate the cost map for this time step
        current_cost_map = calculate_cost_map(current_dynamic_obstacles_pos)
        cost_map_times.append(current_cost_map)

        # Find the A* path
        path = find_a_star_proba(current_cost_map, robot_positions[-1], goal)
        if path is None:
            print(f"No path found at time step {t}. Stopping simulation.")
            break
        path_times.append(path)

        print('PARTH :', path)

         # Move the robot along the path based on remaining distance it can cover in dt
        remaining_distance = robot_speed * dt / 10  # robot speed in m/s, dt in ms, distance in cm 
        for i in range(1, len(path)):
            next_position = path[i]
            distance_to_next_position = heuristic(robot_positions[-1], next_position)
            
            if remaining_distance >= distance_to_next_position:
                # Move fully to the next position
                robot_positions.append(tuple(np.floor(next_position).astype(int)))
                remaining_distance -= distance_to_next_position
            else:
                # Move partially towards the next position
                direction = np.array(next_position) - np.array(robot_positions[-1])
                direction = direction / np.linalg.norm(direction)  # Normalize direction vector
                new_position = np.array(robot_positions[-1]) + direction * remaining_distance
                robot_positions.append(tuple(np.floor(new_position).astype(int)))
                break


        # Check if the goal has been reached (with a small tolerance)
        if heuristic(robot_positions[-1], goal) < 1:  # 1 unit tolerance
            robot_positions[-1] = goal  # Snap to the goal
            goal_reached = True

        # Diagnostic print statements
        print(f"Step {t}:")
        print(f"  - Length of robot_positions: {len(robot_positions)}")
        print(f"  - Length of cost_map_times: {len(cost_map_times)}")
        print(f"  - Length of dynamic_obstacles_times: {len(dynamic_obstacles_times)}")

    # Final check
    print(f"Final lengths:")
    print(f"  - robot_positions: {len(robot_positions)}", robot_positions)
    print(f"  - cost_map_times: {len(cost_map_times)}", cost_map_times)
    print(f"  - dynamic_obstacles_times: {len(dynamic_obstacles_times)}", dynamic_obstacles_times)
    return robot_positions, cost_map_times, dynamic_obstacles_times, path_times


def animate_cost_map(cost_maps, robot_positions, dynamic_obstacles_times, dynamic_obstalcles_dir_speed, goal, time_steps, dt, path_times):
    """
    Create an animation to visualize the robot's movement, dynamic obstacles, and the planned path over time.

    Args:
    - cost_maps (list of numpy arrays): Cost maps at each time step, representing the environment with obstacle probabilities.
    - robot_positions (list of tuples): List of robot positions at each time step, showing the path the robot takes.
    - dynamic_obstacles_times (list of numpy arrays): List of arrays, each containing the predicted positions of dynamic obstacles at each time step.
    - dynamic_obstalcles_dir_speed (list of tuples): List of direction and speed tuples for each obstacle.
    - goal (tuple): The goal position on the map, which the robot is trying to reach.
    - time_steps (int): The number of time steps in the simulation.
    - dt (int): Time interval in milliseconds between each simulation step.
    - path_times (list of lists): List of paths at each time step.

    Returns:
    - FuncAnimation: A Matplotlib animation object that visualizes the robot's navigation, obstacle movements, and the path over time.
    """
    fig, ax = plt.subplots(figsize=(12.8, 10))
    max_frames = min(len(cost_maps), len(robot_positions), len(dynamic_obstacles_times))

    def update(t):
        ax.clear()

        # Ensure we don't exceed the available data
        if t >= max_frames:
            print(f"Warning: Time step {t} exceeds available data. Skipping this frame.")
            return

        # Display the cost map at the current time step
        ax.imshow(cost_maps[t].T, cmap='hot', origin='lower', extent=[-640, 640, 0, 1000])

        # Plot the robot's position as a green 'x'
        robot_position = robot_positions[t]
        ax.plot(robot_position[0], robot_position[1], marker='x', color='green', markersize=15, mew=3)
        
        # Mark the goal position with a magenta 'x'
        ax.plot(goal[0], goal[1], marker='x', color='magenta', markersize=15, mew=3)

        # Plot the positions and directions of dynamic obstacles as blue arrows
        for obstacle_pos, (direction, speed) in zip(dynamic_obstacles_times[t], dynamic_obstalcles_dir_speed):
            ax.arrow(obstacle_pos[0], obstacle_pos[1], np.cos(direction) * 50, np.sin(direction) * 50, 
                     head_width=20, head_length=30, fc='blue', ec='blue')

        # Plot the entire planned path in red
        if path_times[t] is not None and len(path_times[t]) > 1:
            path_x = [pos[0] for pos in path_times[t]]
            path_y = [pos[1] for pos in path_times[t]]
            ax.plot(path_x, path_y, color='#ff6961', linestyle='--', linewidth=2)

        # Plot the robot's path so far as a red line
        if t > 0:
            past_positions_x = [pos[0] for pos in robot_positions[:t+1]]
            past_positions_y = [pos[1] for pos in robot_positions[:t+1]]
            ax.plot(past_positions_x, past_positions_y, color='red', linestyle='-', linewidth=2)

        ax.set_title(f'Time step {t * dt} ms')
        ax.set_xlim([-640, 640])
        ax.set_ylim([0, 1000])

    anim = FuncAnimation(fig, update, frames=int(time_steps/dt), interval=dt)
    return anim


def create_internal_obstacles(num_obstacles):
    """
    Generates a set of obstacles that are initially positioned inside the grid.

    Args:
    - num_obstacles (int): The number of obstacles to create.

    Returns:
    - dynamic_obstacles_pos (numpy array): An array of shape (num_obstacles, 2) containing the initial positions of the obstacles.
      Each position is represented as [x, y] coordinates.
    - dynamic_obstalcles_dir_speed (list of tuples): A list of tuples where each tuple contains:
      - direction (float): The direction of the obstacle's movement in radians.
      - speed (float): The speed of the obstacle in centimeters per second.
    """
    dynamic_obstacles_pos = np.zeros((num_obstacles, 2)) # Initialize obstacle positions
    dynamic_obstalcles_dir_speed = []

    for i in range(num_obstacles):
        initial_x = np.random.uniform(-640, 640)
        initial_y = np.random.uniform(0, 1000)
        
        # Direction remains the same, but speed should be 
        direction = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 1.5)
        
        # Append the position and direction-speed tuple
        dynamic_obstacles_pos[i, :] = [initial_x, initial_y]
        dynamic_obstalcles_dir_speed.append((direction, speed))
    
    return dynamic_obstacles_pos, dynamic_obstalcles_dir_speed