import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import heapq

# Heuristic function for A* pathfinding
def heuristic(a, b, weight=1.5):
    return weight * np.linalg.norm(np.array(a) - np.array(b))

# Cost function that considers the obstacle probability
def modified_cost(current, neighbor, prob_grid):
    base_cost = heuristic(current, neighbor)
    prob_cost = prob_grid[neighbor[0], neighbor[1]]
    return base_cost + 50 * prob_cost

# Calculate the cost map based on dynamic obstacles positions
def calculate_cost_map(dynamic_obstacles_pos, grid_size):
    cost_map = np.zeros(grid_size)
    grid_width, grid_height = grid_size

    def x_to_grid(x):
        return int((x + grid_width / 2) * (grid_width / 1280))  # Adjusting based on grid size

    def y_to_grid(y):
        return int(y * (grid_height / 1000))  # Adjusting based on grid size

    grid_coords = np.array([[x_to_grid(obst[0]), y_to_grid(obst[1])] for obst in dynamic_obstacles_pos])
    grid_coords = np.clip(grid_coords, [0, 0], [grid_width - 1, grid_height - 1])
    radius = 50 * (grid_width / 1280)

    x_indices, y_indices = np.meshgrid(np.arange(grid_width), np.arange(grid_height), indexing='ij')

    for grid_x, grid_y in grid_coords:
        distance_to_center = np.sqrt((x_indices - grid_x) ** 2 + (y_indices - grid_y) ** 2)
        influence = np.where(distance_to_center <= radius, 1 - (distance_to_center / radius), 0)
        cost_map = np.maximum(cost_map, influence)

    return cost_map

# Update positions of dynamic obstacles
def update_dynamic_obstacles(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, dt, grid_size):
    updated_dynamic_obstacles = []
    grid_width, grid_height = grid_size

    for i in range(dynamic_obstacles_pos.shape[0]):
        direction, speed = dynamic_obstalcles_dir_speed[i]
        futur_x = dynamic_obstacles_pos[i, 0] + np.cos(direction) * speed * dt / 1000 * grid_width / 1280
        futur_y = dynamic_obstacles_pos[i, 1] + np.sin(direction) * speed * dt / 1000 * grid_height / 1000
        updated_dynamic_obstacles.append([futur_x, futur_y])

    return np.array(updated_dynamic_obstacles)

# A* pathfinding algorithm
def find_a_star_proba(cost_map, start, goal, max_iterations=1000000):
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

# Simulation function
def simulation(dynamic_obstacles_pos, dynamic_obstalcles_dir_speed, start, goal, robot_speed, time_steps, dt, grid_size):
    robot_positions = [start]
    cost_map_times = []
    path_times = []
    dynamic_obstacles_times = [dynamic_obstacles_pos]
    steps = int(time_steps / dt)
    goal_reached = False
    
    initial_cost_map = calculate_cost_map(dynamic_obstacles_pos, grid_size)
    cost_map_times.append(initial_cost_map)

    for t in range(steps):
        if goal_reached:
            print(f"Goal reached at step {t}.")
            break

        current_dynamic_obstacles_pos = update_dynamic_obstacles(dynamic_obstacles_times[-1], dynamic_obstalcles_dir_speed, dt, grid_size)
        dynamic_obstacles_times.append(current_dynamic_obstacles_pos)

        current_cost_map = calculate_cost_map(current_dynamic_obstacles_pos, grid_size)
        cost_map_times.append(current_cost_map)

        path = find_a_star_proba(current_cost_map, robot_positions[-1], goal)
        if path is None:
            print(f"No path found at time step {t}. Stopping simulation.")
            break
        path_times.append(path)

        remaining_distance = robot_speed * dt / 1000 * (grid_size[0] / 1280)
        for i in range(1, len(path)):
            next_position = path[i]
            distance_to_next_position = heuristic(robot_positions[-1], next_position)
            
            if remaining_distance >= distance_to_next_position:
                robot_positions.append(tuple(np.floor(next_position).astype(int)))
                remaining_distance -= distance_to_next_position
            else:
                direction = np.array(next_position) - np.array(robot_positions[-1])
                direction = direction / np.linalg.norm(direction)
                new_position = np.array(robot_positions[-1]) + direction * remaining_distance
                robot_positions.append(tuple(np.floor(new_position).astype(int)))
                break

        if heuristic(robot_positions[-1], goal) < 1:
            robot_positions[-1] = goal
            goal_reached = True

        print(f"Step {t}:")
        print(f"  - Length of robot_positions: {len(robot_positions)}")
        print(f"  - Length of cost_map_times: {len(cost_map_times)}")
        print(f"  - Length of dynamic_obstacles_times: {len(dynamic_obstacles_times)}")

    print(f"Final lengths:")
    print(f"  - robot_positions: {len(robot_positions)}", robot_positions)
    print(f"  - cost_map_times: {len(cost_map_times)}", cost_map_times)
    print(f"  - dynamic_obstacles_times: {len(dynamic_obstacles_times)}", dynamic_obstacles_times)
    return robot_positions, cost_map_times, dynamic_obstacles_times, path_times
def animate_cost_map(cost_maps, robot_positions, dynamic_obstacles_times, dynamic_obstalcles_dir_speed, goal, time_steps, dt, path_times, grid_size):
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
    - grid_size (tuple): Size of the grid (width, height).

    Returns:
    - FuncAnimation: A Matplotlib animation object that visualizes the robot's navigation, obstacle movements, and the path over time.
    """
    fig, ax = plt.subplots(figsize=(12.8, 10))
    max_frames = min(len(cost_maps), len(robot_positions), len(dynamic_obstacles_times))

    grid_width, grid_height = grid_size

    def update(t):
        ax.clear()

        # Ensure we don't exceed the available data
        if t >= max_frames:
            print(f"Warning: Time step {t} exceeds available data. Skipping this frame.")
            return

        # Display the cost map at the current time step
        ax.imshow(cost_maps[t].T, cmap='hot', origin='lower', extent=[-grid_width/2, grid_width/2, 0, grid_height])

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
        ax.set_xlim([-grid_width/2, grid_width/2])
        ax.set_ylim([0, grid_height])

    anim = FuncAnimation(fig, update, frames=int(time_steps/dt), interval=dt)
    return anim

def create_internal_obstacles(num_obstacles, grid_size):
    """
    Generates a set of obstacles that are initially positioned inside the grid.

    Args:
    - num_obstacles (int): The number of obstacles to create.
    - grid_size (tuple): Size of the grid (width, height).

    Returns:
    - dynamic_obstacles_pos (numpy array): An array of shape (num_obstacles, 2) containing the initial positions of the obstacles.
      Each position is represented as [x, y] coordinates.
    - dynamic_obstalcles_dir_speed (list of tuples): A list of tuples where each tuple contains:
      - direction (float): The direction of the obstacle's movement in radians.
      - speed (float): The speed of the obstacle in centimeters per second.
    """
    dynamic_obstacles_pos = np.zeros((num_obstacles, 2))
    dynamic_obstalcles_dir_speed = []
    
    grid_width, grid_height = grid_size

    for i in range(num_obstacles):
        initial_x = np.random.uniform(-grid_width/2, grid_width/2)
        initial_y = np.random.uniform(0, grid_height)
        direction = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 1.5)
        
        dynamic_obstacles_pos[i, :] = [initial_x, initial_y]
        dynamic_obstalcles_dir_speed.append((direction, speed))
    
    return dynamic_obstacles_pos, dynamic_obstalcles_dir_speed