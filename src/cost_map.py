"""
cost_map.py
Contains functions for creating the cost map based on the 2D top view, directions, and speed.
"""

import numpy as np
import matplotlib.pyplot as plt


def create_cost_map(depths, horizontal_pos, directions, speeds, robot_speed):
    grid_size = (1280, 1000)
    prob_grid = np.zeros(grid_size)
    dynamic_obstacles = []

    # Coordinate conversion functions
    def x_to_grid(x):
        return int(x + 680)  # Convert x from [-680, 680] to [0, 1280]
    
    def y_to_grid(y):
        return int(y)  # y already in [0, 1000]

    for depth, horizontal, direction, speed in zip(depths, horizontal_pos, directions, speeds):
        if (direction is not None) and (depth is not None) and (horizontal is not None) and (speed is not None):
            coordinates = (int(horizontal), int(depth * 100))
            dynamic_obstacles.append((coordinates, direction, speed))
            print('dynamic obstacle', dynamic_obstacles)
            time = 0

            while time < 2000: 
                futur_x = coordinates[0] + np.cos(direction) * speed * time
                futur_y = coordinates[1] + np.sin(direction) * speed * time  

                # Convert future coordinates to grid indices
                grid_x = x_to_grid(futur_x)
                grid_y = y_to_grid(futur_y)

                # Ensure future coordinates are within the grid bounds
                if 0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1]:
                    dist_to_robot = np.sqrt(futur_x**2 + futur_y**2)
                    collision_time_check = dist_to_robot / robot_speed

                    if time - 2.5 < collision_time_check <= time + 2.5:
                        print('Collision FOUND !!!')
                        print(f"Future Position: ({futur_x}, {futur_y})")

                        radius = int(25 + dist_to_robot/10)
                        for i in range(max(0, grid_x - radius), min(grid_size[0], grid_x + radius)):
                            for j in range(max(0, grid_y - radius), min(grid_size[1], grid_y + radius)):
                                distance_to_center = np.sqrt((i - grid_x) ** 2 + (j - grid_y) ** 2)
                                if distance_to_center <= radius:
                                    influence = 1 - (distance_to_center / radius)
                                    prob_grid[i, j] = max(prob_grid[i, j], influence)

                time += 5

    return prob_grid, dynamic_obstacles

def plot_cost_map(prob_grid, dynamic_obstacles):
    """
    Plots the cost map with decreasing colors around obstacles.

    Args:
    - prob_grid (numpy array): Probability grid representing the cost map.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.

    Returns:
    - None
    """
    plt.figure(figsize=(12.8, 10))  # Adjust the figure size to match the physical dimensions
    # Plot the cost map
    plt.imshow(prob_grid.T, cmap='hot', origin='lower', extent=[-680, 680, 0, 1000])
    
    # Plot the obstacles and their directions
    for obstacle in dynamic_obstacles:
        (x, y), direction, speed = obstacle
        cos_dir = np.cos(direction)
        sin_dir = np.sin(direction)
        plt.arrow(x, y, cos_dir * 50, sin_dir * 50, head_width=20, head_length=30, fc='blue', ec='blue')
    
    plt.colorbar(label='Obstacle Influence')
    plt.title('Cost Map with Obstacles')
    plt.xlabel('Horizontal Position (cm)')
    plt.ylabel('Depth (cm)')
    plt.grid(False)
    plt.show()


#------------------------------ NEW COST MAP TIME DEPENDENT ------------------------------#

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def create_time_dependent_cost_map(depths, horizontal_pos, directions, speeds, time_steps=400, dt=5):
    grid_size = (1280, 1000)
    cost_map = np.zeros((grid_size[0], grid_size[1], time_steps))  # 3D cost map: (x, y, time)
    dynamic_obstacles = []

    # Coordinate conversion functions
    def x_to_grid(x):
        return int(x + 680)  # Convert x from [-680, 680] to [0, 1280]
    
    def y_to_grid(y):
        return int(y)  # y already in [0, 1000]

    for depth, horizontal, direction, speed in zip(depths, horizontal_pos, directions, speeds):
        if (direction is not None) and (depth is not None) and (horizontal is not None) and (speed is not None):
            coordinates = (int(horizontal), int(depth * 100))
            dynamic_obstacles.append((coordinates, direction, speed))
            time = 0

            for t in range(time_steps):
                futur_x = coordinates[0] + np.cos(direction) * speed * time
                futur_y = coordinates[1] + np.sin(direction) * speed * time  

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

                time += dt  # Increment time by the time step

    return cost_map, dynamic_obstacles

def plot_all_time_dependent_cost_maps(cost_map, dynamic_obstacles, time_steps=400):
    """
    Plots all the time-dependent cost maps with 3 plots per row.

    Args:
    - cost_map (numpy array): 3D cost map array.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - time_steps (int): The number of time steps to plot.

    Returns:
    - None
    """
    # Determine the number of rows needed
    num_rows = (time_steps + 2) // 3  # Calculate the number of rows needed for 3 plots per row

    plt.figure(figsize=(15, 5 * num_rows))  # Adjust the figure size according to the number of rows

    for t in range(time_steps):
        plt.subplot(num_rows, 3, t + 1)  # Create a subplot for each time step
        
        # Plot the cost map at the given time step
        plt.imshow(cost_map[:, :, t].T, cmap='hot', origin='lower', extent=[-680, 680, 0, 1000])
        
        # Plot the obstacles and their directions
        for obstacle in dynamic_obstacles:
            (x, y), direction, speed = obstacle
            cos_dir = np.cos(direction)
            sin_dir = np.sin(direction)
            plt.arrow(x, y, cos_dir * 50, sin_dir * 50, head_width=20, head_length=30, fc='blue', ec='blue')
        
        plt.colorbar(label='Obstacle Influence')
        plt.title(f'Time step {t * 5} ms')
        plt.xlabel('Horizontal Position (cm)')
        plt.ylabel('Depth (cm)')
        plt.grid(False)
    
    plt.tight_layout()  # Adjust subplots to fit into the figure area
    plt.show()


def animate_cost_map(cost_map, dynamic_obstacles, time_steps=400, interval=100):
    """
    Creates an animation showing the evolution of the cost map over time.

    Args:
    - cost_map (numpy array): 3D cost map array.
    - dynamic_obstacles (list of tuples): List of dynamic obstacles.
    - time_steps (int): The number of time steps to animate.
    - interval (int): Time delay between frames in milliseconds.

    Returns:
    - anim (FuncAnimation): The animation object.
    """
    fig, ax = plt.subplots(figsize=(12.8, 10))
    
    def update(t):
        ax.clear()
        # Plot the cost map at the given time step
        ax.imshow(cost_map[:, :, t].T, cmap='hot', origin='lower', extent=[-680, 680, 0, 1000])
        
        # Plot the obstacles and their directions
        for obstacle in dynamic_obstacles:
            (x, y), direction, speed = obstacle
            cos_dir = np.cos(direction)
            sin_dir = np.sin(direction)
            ax.arrow(x, y, cos_dir * 50, sin_dir * 50, head_width=20, head_length=30, fc='blue', ec='blue')
        
        ax.set_title(f'Time step {t * 5} ms')
        ax.set_xlabel('Horizontal Position (cm)')
        ax.set_ylabel('Depth (cm)')
        ax.grid(False)
        ax.set_xlim([-680, 680])
        ax.set_ylim([0, 1000])
        plt.colorbar(ax.imshow(cost_map[:, :, t].T, cmap='hot', origin='lower', extent=[-680, 680, 0, 1000]), ax=ax, label='Obstacle Influence')

    anim = FuncAnimation(fig, update, frames=time_steps, interval=interval)
    plt.show()
    return anim
