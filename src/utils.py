import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#----------------BOXES----------------#

def draw_boxes(image_path, coords):
    """
    Draws bounding boxes around detected persons in the image.
    
    Args:
    - image_path (str): The file path to the input image.
    - coords (list of tuples): List of coordinates for the bounding boxes.
    
    Returns:
    - image_rgb (numpy array): Image with bounding boxes drawn.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        for idx, (x1, y1, x2, y2) in enumerate(coords):
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f'{idx+1}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)
            x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
            cv2.circle(image, (x_center, y_center), 5, (0, 0, 255), -1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image_rgb
    except Exception as e:
        logging.error(f"An error occurred in draw_boxes with file {image_path}: {e}")

def preprocess_boxes(depth_image, coords):
    """
    Preprocesses the depth image by applying a mask to exclude background.
    
    Args:
    - depth_image (PIL Image): Depth image.
    - coords (list of tuples): List of coordinates for the bounding boxes.
    
    Returns:
    - filtered_images (list of numpy arrays): List of preprocessed depth images.
    """
    try:
        depth_image_np = np.array(depth_image)
        filtered_images = []

        for (x1, y1, x2, y2) in coords:
            cropped_img = depth_image_np[y1:y2, x1:x2]
            filtered_images.append(cropped_img * (cropped_img > 0))  # Apply mask directly

        return filtered_images
    except Exception as e:
        logging.error(f"An error occurred in preprocess_boxes: {e}")
        return []

#----------------DISPLAY IMAGES----------------#

def display_img(img, title="Image"):
    """
    Displays an image using matplotlib.
    
    Args:
    - img (PIL Image or numpy array): Image to display.
    - title (str): Title of the plot.
    """
    try:
        plt.figure(figsize=(6, 6))
        if isinstance(img, Image.Image):
            img = np.array(img)
        if len(img.shape) == 3:
            plt.imshow(img)
        else:
            plt.imshow(img, cmap='gray')
        plt.title(title)
        plt.xticks([])
        plt.yticks([])
        plt.show()
    except Exception as e:
        logging.error(f"An error occurred in display_img: {e}")

def display_cropped_images(cropped_images):
    """
    Displays a list of cropped images using matplotlib.
    
    Args:
    - cropped_images (list of numpy arrays): List of cropped images to display.
    """
    try:
        num_images = len(cropped_images)
        fig, axes = plt.subplots(1, num_images, figsize=(15, 5))
        if num_images == 1:
            axes = [axes]
        for i, cropped_img in enumerate(cropped_images):
            if len(cropped_img.shape) == 3:
                axes[i].imshow(cropped_img)
            else:
                axes[i].imshow(cropped_img, cmap='gray')
            axes[i].set_title(f"{i+1}")
            axes[i].axis('off')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        logging.error(f"An error occurred in display_cropped_images: {e}")

def combine_and_save_images(depth_image, boxed_image, output_path):
    """
    Combines depth and boxed images side by side and saves the result.
    
    Args:
    - depth_image (PIL Image): Depth image.
    - boxed_image (numpy array): Image with bounding boxes.
    - output_path (str): File path to save the combined image.
    """
    try:
        depth_image_np = cv2.cvtColor(np.array(depth_image), cv2.COLOR_GRAY2RGB) 

        if depth_image_np.shape != boxed_image.shape:
            boxed_image = cv2.resize(boxed_image, (depth_image_np.shape[1], depth_image_np.shape[0])) 

        combined_image = np.hstack((depth_image_np, boxed_image)) 
        combined_pil_image = Image.fromarray(combined_image)  
        combined_pil_image.save(output_path)  
        print(f"Combined image saved to {output_path}") 
    except Exception as e:
        logging.error(f"An error occurred in combine_and_save_images: {e}")

def display_original_and_depth(image_path, depth_image, coords):
    """
    Displays the original image with bounding boxes, depth image, and depth image with bounding boxes.

    Args:
    - image_path (str): The file path to the input image.
    - depth_image (PIL Image): Depth image.
    - coords (list of tuples): List of coordinates for the bounding boxes.
    """
    try:
        original_image = cv2.imread(image_path)
        depth_image_np = np.array(depth_image)

        # Draw bounding boxes on the original image
        for idx, (x1, y1, x2, y2) in enumerate(coords):
            cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(original_image, f'{idx+1}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
            cv2.circle(original_image, (x_center, y_center), 5, (0, 0, 255), -1)

        # Draw bounding boxes on the depth image
        depth_image_with_boxes = cv2.cvtColor(depth_image_np, cv2.COLOR_GRAY2BGR)
        for idx, (x1, y1, x2, y2) in enumerate(coords):
            cv2.rectangle(depth_image_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(depth_image_with_boxes, f'{idx+1}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
            cv2.circle(depth_image_with_boxes, (x_center, y_center), 5, (0, 0, 255), -1)

        fig, axes = plt.subplots(1, 3, figsize=(20, 5))

        axes[0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        axes[0].set_title('Original Image with Boxes')
        axes[0].axis('off')

        axes[1].imshow(depth_image_np, cmap='plasma')
        axes[1].set_title('Depth Image')
        axes[1].axis('off')

        axes[2].imshow(depth_image_with_boxes)
        axes[2].set_title('Depth Image with Boxes')
        axes[2].axis('off')

        plt.tight_layout()
        plt.show()
    except Exception as e:
        logging.error(f"An error occurred in display_original_and_depth: {e}")


def resize_with_padding(image, target_size):
    """
    Resizes the image with padding to fit the target size.

    Args:
    - image (numpy array): The input image.
    - target_size (int): The target size for resizing.

    Returns:
    - padded_image (numpy array): The padded and resized image.
    - scale (float): The scaling factor used for resizing.
    - pad_h (int): The padding height.
    - pad_w (int): The padding width.
    """
    h, w, _ = image.shape
    scale = target_size / max(h, w)
    nh, nw = int(h * scale), int(w * scale)
    resized_image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_LINEAR)
    pad_h = (target_size - nh) // 2
    pad_w = (target_size - nw) // 2
    padded_image = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    padded_image[pad_h:pad_h + nh, pad_w:pad_w + nw, :] = resized_image
    return padded_image, scale, pad_h, pad_w


def resize_to_x_by_x(image, new_size):
    """
    Resizes the image to 1024x1024 pixels.

    Args:
    - image (numpy array): The input image.

    Returns:
    - resized_image (numpy array): The resized image.
    """
    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)
    return resized_image

#-------------------RANDOM----------------------

def calculate_pixel_value(filtered_depth_images):
    """
    Calculates the average pixel value for each filtered depth image.

    Args:
    - filtered_depth_images (list of numpy arrays): List of preprocessed depth images.

    Returns:
    - pixel_value (list of floats): List of average pixel value for each person.
    """
    try:
        pixel_value = [np.mean(img[img > 0]) for img in filtered_depth_images]
        return pixel_value
    except Exception as e:
        logging.error(f"An error occurred in calculate_pixel_value: {e}")
        return []

def horizontal_pixel_pos(coords):
    """
    Calculates the horizontal pixel positions for each bounding box.

    Args:
    - coords (list of tuples): List of coordinates for the bounding boxes.

    Returns:
    - horizontal_pos (list of floats): List of horizontal positions for each bounding box.
    """
    try:
        horizontal_pos = []
        for (x1, y1, x2, y2) in coords:
            x_center = (x1 + x2) / 2
            horizontal_pos.append(x_center)
        return horizontal_pos
    except Exception as e:
        logging.error(f"An error occurred in horizontal_pixel_pos: {e}")

def horizontal_pos_conversion(horizontal_pos_in_pixel):
    """
    Translate the horizontal pixel positions to the position in cm centered around the robot.

    Args:
    - horizontal_pos_in_pixel (list or array-like): List of horizontal pixel positions.

    Returns:
    - numpy array: Array of positions in cm centered around the robot.
    """
    horizontal_pos_in_pixel = np.array(horizontal_pos_in_pixel)
    
    centered_horizontal_pos_in_pixel = horizontal_pos_in_pixel - 680

    pos_in_cm_centered = centered_horizontal_pos_in_pixel
    
    return np.array(pos_in_cm_centered)
    

def rational_func(x, a, b, c):
    """ Rational function for curve fitting. """
    return a / (x + b) + c

def exponential_func(x, a, b, c):
    """ Exponential function for curve fitting. """
    return a * np.exp(b * x) + c

def power_law_func(x, a, b):
    """ Power-law function for curve fitting. """
    return a * np.power(x, b)

def find_closest_person(depths, coords):
    """
    Finds the closest person based on average depth.
    
    Args:
    - depths (list of floats): List of average depths for each person.
    - coords (list of tuples): List of coordinates for detected persons.
    
    Returns:
    - closest_coord (tuple): Coordinates of the closest person.
    - closest_depth (float): Average depth of the closest person.
    """
    try:
        closest_idx = np.argmax(depths)  
        closest_coord = coords[closest_idx] 
        return closest_coord, depths[closest_idx]
    except Exception as e:
        logging.error(f"An error occurred in find_closest_person: {e}")

def predict_distance(pixel_value, model_params, model_type='rational'):
    """
    Predicts the distance based on the pixel value using the specified model.

    Args:
    - pixel_value (float): The pixel value to be used for prediction.
    - model_params (tuple): Parameters of the chosen model.
    - model_type (str): The type of the model ('rational', 'exponential', 'power', 'polynomial').

    Returns:
    - distance (float): Predicted distance.
    """
    try:
        if model_type == 'rational':
            return rational_func(pixel_value, *model_params)
        elif model_type == 'exponential':
            return exponential_func(pixel_value, *model_params)
        elif model_type == 'power':
            return power_law_func(pixel_value, *model_params)
        elif model_type == 'polynomial':
            poly_model = np.poly1d(model_params)
            return poly_model(pixel_value)
        else:
            raise ValueError("Invalid model type specified.")
    except Exception as e:
        logging.error(f"An error occurred in predict_distance: {e}")


def get_image_size(img_path):
    """
    Gets the size of the image.

    Args:
    - img_path (str): Path to the image.

    Returns:
    - size_img (tuple): Size of the image (width, height).
    """
    image = cv2.imread(img_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {img_path}")
    height, width, _ = image.shape
    return image, (width, height)


def create_hardcoded_obstacle(initial_position, direction, speed, time_steps=100, dt=10):
    """
    Creates a hardcoded obstacle's future positions based on an initial position, direction, and speed.

    Args:
    - initial_position (tuple of int): The initial position of the obstacle (x, y) in the coordinate space (-640, 640), (0, 1000).
    - direction (float): The direction of the obstacle's movement in radians.
    - speed (float): The speed of the obstacle in centimeters per second.
    - time_steps (int, optional): The number of time steps to simulate. Default is 100.
    - dt (int, optional): The time increment (in milliseconds) between each time step. Default is 10 ms.

    Returns:
    - obstacle (tuple): A tuple where each tuple contains:
      - coordinates (numpy array of shape (time_steps, 2)): A 2D array with the future coordinates of the obstacle for each time step.
      - direction (float): The direction of the obstacle's movement in radians.
      - speed (float): The speed of the obstacle in centimeters per second.
    """
    initial_coordinates = np.array(initial_position, dtype=int)
    future_coordinates = np.zeros((time_steps, 2), dtype=int)  # 2D array to store future positions as integers

    for t in range(time_steps):
        futur_x = int(initial_coordinates[0] + np.cos(direction) * speed * t * dt)
        futur_y = int(initial_coordinates[1] + np.sin(direction) * speed * t * dt)
        future_coordinates[t] = [futur_x, futur_y]

    # Return the obstacle as a tuple with its future positions, direction, and speed
    obstacle = (future_coordinates, direction, speed)
    return obstacle

import numpy as np

# Function to create obstacles already inside the grid
def create_internal_obstacles(num_obstacles):
    dynamic_obstacles_pos = np.zeros((num_obstacles, 2))  # No extra dimension here
    dynamic_obstalcles_dir_speed = []
    
    for i in range(num_obstacles):
        initial_x = np.random.uniform(-640, 640)
        initial_y = np.random.uniform(0, 1000)
        direction = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(0.5, 1.5)
        
        dynamic_obstacles_pos[i, :] = [initial_x, initial_y]
        dynamic_obstalcles_dir_speed.append((direction, speed))
    
    return dynamic_obstacles_pos, dynamic_obstalcles_dir_speed


def create_entry_obstacles(num_obstacles, grid_size, entry_speed, time_steps=100, dt=10, max_delay=100):
    """
    Creates obstacles that enter the grid from the edges over time with staggered start times.

    Args:
    - num_obstacles (int): Number of obstacles to create.
    - grid_size (tuple): Size of the grid (width, height).
    - entry_speed (float): Speed of the obstacles entering the grid (cm/s).
    - time_steps (int, optional): Number of time steps for the simulation. Default is 100.
    - dt (int, optional): Time increment between steps in milliseconds. Default is 10 ms.
    - max_delay (int, optional): Maximum delay (in time steps) before the obstacle starts entering the grid.

    Returns:
    - dynamic_obstacles (list of tuples): List of obstacles with their positions and movements.
    """
    
    for _ in range(num_obstacles):
        # Randomly choose an entry side: 0=left, 1=right, 2=top, 3=bottom
        side = np.random.choice([0, 1, 2, 3])
        if side == 0:  # Left edge
            initial_x = -650  # Just outside the grid
            initial_y = np.random.uniform(0, grid_size[1])  # Random y position
            direction = np.random.uniform(-np.pi / 4, np.pi / 4)  # Moving right
        elif side == 1:  # Right edge
            initial_x = 650  # Just outside the grid
            initial_y = np.random.uniform(0, grid_size[1])  # Random y position
            direction = np.random.uniform(3 * np.pi / 4, 5 * np.pi / 4)  # Moving left
        elif side == 2:  # Top edge
            initial_x = np.random.uniform(-640, 640)  # Random x position
            initial_y = 1050  # Just outside the grid
            direction = np.random.uniform(-3 * np.pi / 4, -np.pi / 4)  # Moving down
        else:  # Bottom edge
            initial_x = np.random.uniform(-640, 640)  # Random x position
            initial_y = -50  # Just outside the grid
            direction = np.random.uniform(np.pi / 4, 3 * np.pi / 4)  # Moving up
        
        speed = entry_speed
        initial_coordinates = np.array([int(initial_x), int(initial_y)])
        future_coordinates = np.zeros((time_steps, 2), dtype=int)
        
        # Add a random delay before the obstacle starts moving
        delay = np.random.randint(0, max_delay)
        
        # for t in range(time_steps):
        #    if t < delay:
        #        # Before the delay, the obstacle stays outside the grid
        #        future_coordinates[t] = [initial_x, initial_y]
        #    else:
        #        # After the delay, the obstacle starts moving into the grid
        #        futur_x = int(initial_coordinates[0] + np.cos(direction) * speed * (t - delay) * dt)
        #        futur_y = int(initial_coordinates[1] + np.sin(direction) * speed * (t - delay) * dt)
        #        future_coordinates[t] = [futur_x, futur_y]
        
        dynamic_obstacles = (future_coordinates, direction, speed)
    
    return dynamic_obstacles

