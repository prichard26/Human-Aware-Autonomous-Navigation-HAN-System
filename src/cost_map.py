import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def create_time_dependent_cost_map(depths, horizontal_pos, directions, speeds, time_steps=100, dt=10):
    """
    Creates a time-dependent 3D cost map based on the detected positions, directions, and speeds of obstacles.

    Args:
    - depths (list of float): List of depths (in meters) for each obstacle detected.
    - horizontal_pos (list of float): List of horizontal positions (in centimeters) for each obstacle.
    - directions (list of float): List of directions (in radians) for each obstacle's movement.
    - speeds (list of float): List of speeds (in centimeters per second) for each obstacle.
    - time_steps (int, optional): The number of time steps to simulate. Default is 400.
    - dt (int, optional): The time increment (in milliseconds) between each time step. Default is 5 ms.

    Returns:
    - cost_map (numpy array): A 3D numpy array of shape (1280, 1000, time_steps) representing the probability of an obstacle being present at each cell over time.
    - dynamic_obstacles (list of tuples): A list of tuples where each tuple contains:
      - coordinates (numpy array of shape (time_steps, 2)): A 2D array with the future coordinates of the obstacle for each time step.
      - direction (float): The direction of the obstacle's movement in radians.
      - speed (float): The speed of the obstacle in centimeters per second.
    """
    grid_size = (1280, 1000)
    cost_map = np.zeros((grid_size[0], grid_size[1], time_steps))  # 3D cost map: (x, y, time)
    dynamic_obstacles = []

    # Coordinate conversion functions
    def x_to_grid(x):
        return int(x + 640)  # Convert x from [-640, 640] to [0, 1280]
    
    def y_to_grid(y):
        return int(y)  # y already in [0, 1000]

    for depth, horizontal, direction, speed in zip(depths, horizontal_pos, directions, speeds):
        if direction is not None and depth is not None and horizontal is not None and speed is not None:
            initial_coordinates = np.array([int(horizontal), int(depth * 100)])
            future_coordinates = np.zeros((time_steps, 2), dtype=int)  # 2D array to store future positions as integers

            for t in range(time_steps):
                futur_x = int(initial_coordinates[0] + np.cos(direction) * speed * t * dt)
                futur_y = int(initial_coordinates[1] + np.sin(direction) * speed * t * dt)
                future_coordinates[t] = [futur_x, futur_y]

                # Convert future coordinates to grid indices
                grid_x = x_to_grid(futur_x)
                grid_y = y_to_grid(futur_y)

                # Ensure future coordinates are within the grid bounds
                if 0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1]:
                    radius = 25  # Static influence radius around the obstacle
                    for i in range(max(0, grid_x - radius), min(grid_size[0], grid_x + radius)):
                        for j in range(max(0, grid_y - radius), min(grid_size[1], grid_y + radius)):
                            distance_to_center = np.sqrt((i - grid_x) ** 2 + (j - grid_y) ** 2)
                            if distance_to_center <= radius:
                                influence = 1 - (distance_to_center / radius)
                                cost_map[i, j, t] = max(cost_map[i, j, t], influence)

            # Store the obstacle's future positions along with its direction and speed
            dynamic_obstacles.append((future_coordinates, direction, speed))

    return cost_map, dynamic_obstacles


def plot_all_time_dependent_cost_maps(cost_map, dynamic_obstacles, time_steps=100, plots_per_figure=9, dt=10):
    """
    Plots all the time-dependent cost maps with a limit on plots per figure.

    Args:
    - cost_map (numpy array): 3D cost map array.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - time_steps (int): The number of time steps to plot.
    - plots_per_figure (int): Number of plots per figure.
    - dt (int): Time interval between steps (in milliseconds).

    Returns:
    - None
    """
    num_figures = (time_steps + plots_per_figure - 1) // plots_per_figure  # Calculate the number of figures needed

    for f in range(num_figures):
        plt.figure(figsize=(15, 5 * (plots_per_figure // 3)))
        for i in range(plots_per_figure):
            t = f * plots_per_figure + i
            if t >= time_steps:
                break
            plt.subplot(3, 3, i + 1)  # Create a subplot (3 rows by 3 columns)
            plt.imshow(cost_map[:, :, t].T, cmap='hot', origin='lower', extent=[-640, 640, 0, 1000])
            
            # Plot the obstacles and their directions based on pre-calculated future positions
            for coordinates, direction, speed in dynamic_obstacles:
                futur_x, futur_y = coordinates[t]  # Get the coordinates at time t

                # Ensure the arrow is within bounds
                if -640 <= futur_x <= 640 and 0 <= futur_y <= 1000:
                    cos_dir = np.cos(direction)
                    sin_dir = np.sin(direction)
                    plt.arrow(futur_x, futur_y, cos_dir * 50, sin_dir * 50, head_width=20, head_length=30, fc='blue', ec='blue')
            
            plt.title(f'Time step {t * dt} ms')
            plt.xlabel('Horizontal Position (cm)')
            plt.ylabel('Depth (cm)')
            plt.grid(False)
        
        plt.tight_layout()
        plt.show()
     
def animate_cost_map(cost_map, dynamic_obstacles, time_steps=100, dt=10, interval=100):
    """
    Creates an animation showing the evolution of the cost map over time.

    Args:
    - cost_map (numpy array): 3D cost map array.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - time_steps (int): The number of time steps to animate.
    - dt (int): Time interval between steps (in milliseconds).
    - interval (int): Delay between frames in milliseconds.

    Returns:
    - anim (FuncAnimation): The animation object.
    """
    fig, ax = plt.subplots(figsize=(12.8, 10))

    def update(t):
        ax.clear()
        ax.imshow(cost_map[:, :, t].T, cmap='hot', origin='lower', extent=[-640, 640, 0, 1000])
        
        # Plot the obstacles and their directions based on pre-calculated future positions
        for coordinates, direction, speed in dynamic_obstacles:
            futur_x, futur_y = coordinates[t]  # Get the coordinates at time t
            
            # Ensure the arrow is within bounds
            if -640 <= futur_x <= 640 and 0 <= futur_y <= 1000:
                cos_dir = np.cos(direction)
                sin_dir = np.sin(direction)
                ax.arrow(futur_x, futur_y, cos_dir * 50, sin_dir * 50, head_width=20, head_length=30, fc='blue', ec='blue')
        
        ax.set_title(f'Time step {t * dt} ms')
        ax.set_xlabel('Horizontal Position (cm)')
        ax.set_ylabel('Depth (cm)')
        ax.grid(False)
        ax.set_xlim([-640, 640])
        ax.set_ylim([0, 1000])

    anim = FuncAnimation(fig, update, frames=time_steps, interval=interval)
    
    # Display the animation in the notebook
    return anim