import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import heapq

SCALE = 0.3


def x_to_grid(x):
    """Convert x coordinate from world space to grid space."""
    return int(x + int(640*SCALE))  # Convert x from [-640*SCALE, 640*SCALE] to [0, 1280*SCALE]

def grid_to_x(grid):
    """Convert x coordinate from grid space to world space."""
    return int(grid - int(640*SCALE))  # Convert x from [0, 1280*SCALE] to [-640*SCALE, 640*SCALE]

def y_to_grid(y):
    """Convert y coordinate from world space to grid space."""
    return int(y)  # y already in [0, 1000*SCALE]

def heuristic(a, b, weight=1):
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
    return base_cost + 100 * prob_cost

def calculate_cost_map(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, grid_size=(int(1280*SCALE), int(1000*SCALE))):
    """
    Generate a cost map based on the positions and directions of dynamic obstacles at a certain time.
    
    Args:
    - dynamic_obstacles_pos (numpy array): Array containing the positions of dynamic obstacles.
    - dynamic_obstalcles_dir_speed (list of tuples): List containing the direction and speed of each obstacle.
    - grid_size (tuple): Size of the grid (width, height).
    
    Returns:
    - numpy array: 2D array representing the current cost map.
    """
    cost_map = np.zeros(grid_size)
    
    if dynamic_obstacles_pos.size == 0:
        # No obstacles, return an empty cost map
        return cost_map

    # Convert obstacle positions to grid coordinates
    grid_coords = np.array([[x_to_grid(obst[0]), y_to_grid(obst[1])] for obst in dynamic_obstacles_pos])

    # Ensure all obstacle positions are within the grid boundaries
    grid_coords = np.clip(grid_coords, [0, 0], [grid_size[0] - 1, grid_size[1] - 1])

    # Create a grid of x and y coordinates
    x_indices, y_indices = np.meshgrid(np.arange(grid_size[0]), np.arange(grid_size[1]), indexing='ij')

    for (grid_x, grid_y), (direction, speed) in zip(grid_coords, dynamic_obstalcles_dir_speed):

        # Define the size of the ellipse
        a = int(100*SCALE)  # Length of the ellipse in the direction of movement
        b = int(60*SCALE)   # Width of the ellipse perpendicular to the direction of movement
        B = int(60*SCALE)   # Distance to shift the center of the ellipse

        # Check if a or b is zero
        if a == 0 or b == 0:
            continue  # Skip this obstacle if the ellipse dimensions are zero

        # Calculate new x, y after shifting in the direction of the ellipse
        shifted_x = grid_x + int(B * np.cos(direction))
        shifted_y = grid_y + int(B * np.sin(direction))

        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                # Translate grid points to the shifted ellipse's local coordinate system
                dx = i - shifted_x
                dy = j - shifted_y
                dx_rot = dx * np.cos(direction) + dy * np.sin(direction)
                dy_rot = -dx * np.sin(direction) + dy * np.cos(direction)

                # Avoid division by zero or invalid values
                try:
                    condition = (dx_rot**2 / a**2 + dy_rot**2 / b**2)
                except ZeroDivisionError:
                    continue

                # Check if the point is within the shifted ellipse
                if condition <= 1:
                    # Calculate influence based on the distance from the original coordinates
                    distance_from_original = np.sqrt((i - grid_x) ** 2 + (j - grid_y) ** 2)
                    influence = 1 - (distance_from_original / a)
                    cost_map[i, j] = max(cost_map[i, j], influence)

    return cost_map

def update_dynamic_obstacles(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, dt, grid_size=(int(1280*SCALE), int(1000*SCALE))):
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
    updated_dir_speed = []

    for i in range(num_obstacles):
        direction, speed = dynamic_obstalcles_dir_speed[i]
        
        # Calculate the new positions for each obstacle
        futur_x = dynamic_obstacles_pos[i, 0] + np.cos(direction) * speed * SCALE * dt / 10
        futur_y = dynamic_obstacles_pos[i, 1] + np.sin(direction) * speed * SCALE * dt / 10

        # Check if the obstacle is within the grid boundaries
        if -grid_size[0] / 2 <= futur_x < grid_size[0] / 2 and 0 <= futur_y < grid_size[1]:
            updated_dynamic_obstacles.append([futur_x, futur_y])
            updated_dir_speed.append((direction, speed))  # Add the corresponding direction and speed

    # Ensure both lists have the same length
    assert len(updated_dynamic_obstacles) == len(updated_dir_speed), "Mismatch between positions and direction-speed pairs."

    return np.array(updated_dynamic_obstacles), updated_dir_speed


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
    # Input validation
    if cost_map is None or cost_map.size == 0:
        print("Error: Invalid cost map provided")
        return None
    
    if start is None or goal is None:
        print("Error: Invalid start or goal position")
        return None
    
    # Convert start and goal to grid coordinates first
    start_grid = (x_to_grid(start[0]), y_to_grid(start[1]))
    goal_grid = (x_to_grid(goal[0]), y_to_grid(goal[1]))
    
    # Check if start and goal are within bounds (using grid coordinates)
    if (start_grid[0] < 0 or start_grid[0] >= cost_map.shape[0] or 
        start_grid[1] < 0 or start_grid[1] >= cost_map.shape[1]):
        print(f"Error: Start position {start} -> grid {start_grid} is out of bounds (grid size: {cost_map.shape})")
        return None
        
    if (goal_grid[0] < 0 or goal_grid[0] >= cost_map.shape[0] or 
        goal_grid[1] < 0 or goal_grid[1] >= cost_map.shape[1]):
        print(f"Error: Goal position {goal} -> grid {goal_grid} is out of bounds (grid size: {cost_map.shape})")
        return None
    prob_grid = cost_map
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    close_set = set()
    came_from = {}
    gscore = {start_grid: 0}
    fscore = {start_grid: heuristic(start_grid, goal_grid)}
    open_heap = []
    heapq.heappush(open_heap, (fscore[start_grid], start_grid))
    
    iterations = 0
    
    while open_heap:
        iterations += 1
        if iterations > max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations}), aborting...")
            # Return partial path if available
            if came_from:
                path = []
                current = min(came_from.keys(), key=lambda x: heuristic(x, goal_grid))
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_grid)
                print(f"Returning partial path with {len(path)} waypoints")
                return path[::-1]
            return None
        
        current = heapq.heappop(open_heap)[1]
        
        if np.linalg.norm(np.array(current) - np.array(goal_grid)) <= 1:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_grid)
            print(f"Path found with {len(path)} waypoints in {iterations} iterations")
            return path[::-1]
        
        close_set.add(current)
        
        for i, j in neighbors:
            neighbor = int(current[0] + i), int(current[1] + j)  # Ensure neighbor is an integer tuple
            if 0 <= neighbor[0] < prob_grid.shape[0] and 0 <= neighbor[1] < prob_grid.shape[1]:
                tentative_g_score = gscore[current] + modified_cost(current, neighbor, prob_grid)

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                    continue
                    
                if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_heap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal_grid)
                    heapq.heappush(open_heap, (fscore[neighbor], neighbor))

    return None


def simulation(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, start, goal, robot_speed, time_steps, dt):
    """
    Simulate the robot's movement while avoiding dynamic obstacles.

    Args:
    - dynamic_obstacles_pos (numpy array): Initial positions of obstacles (num_obstacles, 2).
    - dynamic_obstalcles_dir_speed (list of tuples): List containing the direction and speed of each obstacle.
    - start (tuple): Starting position of the robot (x, y).
    - goal (tuple): Goal position (x, y).
    - robot_speed (float): Speed of the robot in meters per second.
    - time_steps (int): Number of time steps for the simulation.
    - dt (int): Time increment between steps in milliseconds.

    Returns:
    - tuple: Containing robot positions over time, cost maps over time, obstacle positions over time, and the path.
    """
    robot_positions = [start]
    cost_map_times = []
    path_times = []
    dynamic_obstacles_times = [dynamic_obstacles_pos]  # Start with initial obstacle positions
    dynamic_obstalcles_dir_speed_times = [dynamic_obstalcles_dir_speed]  # Store initial directions and speeds
    steps = int(time_steps / dt)
    goal_reached = False

    # Calculate and store the initial cost map (at time step 0)
    initial_cost_map = calculate_cost_map(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed)
    cost_map_times.append(initial_cost_map)

    for t in tqdm(range(steps), desc="Simulation Progress"):
        if goal_reached:
            break

        # Update obstacle positions and directions
        current_dynamic_obstacles_pos, dynamic_obstalcles_dir_speed = update_dynamic_obstacles(
            dynamic_obstacles_times[-1], dynamic_obstalcles_dir_speed, dt)
        dynamic_obstacles_times.append(current_dynamic_obstacles_pos)
        dynamic_obstalcles_dir_speed_times.append(dynamic_obstalcles_dir_speed)  # Store updated directions and speeds

        # Calculate the cost map for this time step
        current_cost_map = calculate_cost_map(current_dynamic_obstacles_pos, dynamic_obstalcles_dir_speed)
        cost_map_times.append(current_cost_map)

        # Find the A* path
        path = find_a_star_proba(current_cost_map, robot_positions[-1], goal)
        if path is None:
            print(f"No path found at time step {t}. Stopping simulation.")
            break
        path_times.append(path)

        # Move the robot as far as possible in a single iteration
        remaining_distance = robot_speed * dt / 10  # Calculate the total distance the robot can move in dt
        current_position = np.array(robot_positions[-1])

        while remaining_distance > 0 and len(path) > 1:
            next_position = np.array(path[1])  # Consider the next position in the path
   
            distance_to_next_position = heuristic(current_position, next_position)

            if remaining_distance >= distance_to_next_position:
                # Move completely to the next position
                current_position = next_position
                remaining_distance -= distance_to_next_position
                path.pop(0)  # Remove the point from the path once it's reached
            else:
                # Move partially to the next position
                direction = next_position - (x_to_grid(current_position[0]), y_to_grid(current_position[1]))
                direction = direction / np.linalg.norm(direction)  # Normalize the direction vector
                current_position = current_position + direction * remaining_distance
                remaining_distance = 0  # The robot has used up all its movement distance

        # Add the final position reached by the robot
        robot_positions.append(tuple(np.round(current_position).astype(int)))
        
        # Check if the robot will pass the goal within this time step
        if heuristic(current_position, goal) <= remaining_distance:
            current_position = goal
            goal_reached = True
            break

    return robot_positions, cost_map_times, dynamic_obstacles_times, path_times, dynamic_obstalcles_dir_speed_times


def animate_cost_map(cost_maps, robot_positions, dynamic_obstacles_times, dynamic_obstalcles_dir_speed_times, goal, simulation_time, dt, path_times):
    """
    Create an animation to visualize the robot's movement, dynamic obstacles, and the planned path over time.

    Args:
    - cost_maps (list of numpy arrays): Cost maps at each time step, representing the environment with obstacle probabilities.
    - robot_positions (list of tuples): List of robot positions at each time step, showing the path the robot takes.
    - dynamic_obstacles_times (list of numpy arrays): List of arrays, each containing the predicted positions of dynamic obstacles at each time step.
    - dynamic_obstalcles_dir_speed (list of tuples): List of direction and speed tuples for each obstacle.
    - goal (tuple): The goal position on the map, which the robot is trying to reach.
    - simulation_time (int): The lenght of simulation in ms.
    - dt (int): Time interval in milliseconds between each simulation step.
    - path_times (list of lists): List of paths at each time step.

    Returns:
    - FuncAnimation: A Matplotlib animation object that visualizes the robot's navigation, obstacle movements, and the path over time.
    """    
    fig, ax = plt.subplots(figsize=(12.8, 10))
    max_frames = min(len(cost_maps), len(robot_positions), len(dynamic_obstacles_times), len(path_times))

    def update(t):
        ax.clear()

        # Ensure we don't exceed the available data
        if t >= max_frames:
            return

        # Display the cost map at the current time step
        ax.imshow(cost_maps[t].T, cmap='hot', origin='lower', extent=[int(-640*SCALE), int(640*SCALE), int(0*SCALE), int(1000*SCALE)])

        # Plot the robot's position as a green 'x'
        robot_position = robot_positions[t]
        ax.plot(robot_position[0], robot_position[1], marker='x', color='green', markersize=15, mew=3)
        
        # Mark the goal position with a magenta 'x'
        ax.plot(goal[0], goal[1], marker='x', color='magenta', markersize=15, mew=3)

        # Plot the positions and directions of dynamic obstacles as blue arrows
        for obstacle_pos, direction_speed in zip(dynamic_obstacles_times[t], dynamic_obstalcles_dir_speed_times[t]):
            if isinstance(direction_speed, tuple) and len(direction_speed) == 2:
                direction, speed = direction_speed
                ax.arrow(obstacle_pos[0], obstacle_pos[1], np.cos(direction) * int(50*SCALE), np.sin(direction) * int(50*SCALE), 
                         head_width=int(20*SCALE), head_length=int(30*SCALE), fc='blue', ec='blue')
            else:
                print(f"Invalid direction-speed pair at time step {t}: {direction_speed}")

        # Plot the entire planned path in red
        if path_times[t] is not None and len(path_times[t]) > 1:
            path_x = [(grid_to_x(pos[0])) for pos in path_times[t]]
            path_y = [pos[1] for pos in path_times[t]]
            ax.plot(path_x, path_y, color='#ff6961', linestyle='--', linewidth=2)

        # Plot the robot's path so far as a red line
        if t > 0:
            past_positions_x = [pos[0] for pos in robot_positions[:t+1]]
            past_positions_y = [pos[1] for pos in robot_positions[:t+1]]
            ax.plot(past_positions_x, past_positions_y, color='red', linestyle='-', linewidth=2)

        ax.set_title(f'Time step {t * dt} ms')
        ax.set_xlim([int(-640*SCALE), int(640*SCALE)])
        ax.set_ylim([int(0*SCALE), int(1000*SCALE)])

    anim = FuncAnimation(fig, update, frames=max_frames, interval=dt)
    return anim

def create_internal_obstacles(num_obstacles):
    """
    Generates a set of obstacles that are initially positioned inside the grid.

    Args:
    - num_obstacles (int): The number of obstacles to create.

    Returns:
    - dynamic_obstacles_pos (numpy array): An array of shape (num_obstacles, 1, 2) containing the initial positions of the obstacles.
      Each position is represented as [x, y] coordinates.
    - dynamic_obstalcles_dir_speed (list of tuples): A list of tuples where each tuple contains:
      - direction (float): The direction of the obstacle's movement in radians.
      - speed (float): The speed of the obstacle in centimeters per second.

    The function generates random initial positions for the obstacles within the grid's boundaries.
    It also assigns a random direction and speed to each obstacle.
    """
    dynamic_obstacles_pos = np.zeros((num_obstacles, 2))  # No extra dimension here
    dynamic_obstalcles_dir_speed = []
    
    for i in range(num_obstacles):
        initial_x = int(np.random.uniform(int(-620*SCALE), int(620*SCALE)))
        initial_y = int(np.random.uniform(int(20*SCALE), int(980*SCALE)))
        direction = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 1.5)
        
        dynamic_obstacles_pos[i, :] = [initial_x, initial_y]
        dynamic_obstalcles_dir_speed.append((direction, speed))
    
    return dynamic_obstacles_pos, dynamic_obstalcles_dir_speed