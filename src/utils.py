import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import logging
import tensorflow as tf

# Dictionary of keypoint indices
keypoint_indices = {
    'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
    'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
    'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
    'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
}

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

def predict_distance(pixel_value, model_params, model_type='polynomial'):
    """
    Predicts the distance based on the pixel value using the specified model in [cm].

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
            return exponential_func(pixel_value, *model_params)*100
        elif model_type == 'power':
            return power_law_func(pixel_value, *model_params)*100
        elif model_type == 'polynomial':
            poly_model = np.poly1d(model_params)
            return poly_model(pixel_value)*100
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


def extract_and_scale_keypoints(image, posenet_model):
    """
    Extract keypoints using PoseNet and scale them back to the original image size.

    Args:
    - image (numpy array): The original input image.
    - posenet_model (model): The PoseNet model used for keypoint detection.

    Returns:
    - keypoints_scaled (dict): Scaled keypoints with the structure:
      {
        'nose': (x, y), 'left_eye': (x, y), 'right_eye': (x, y), 'left_ear': (x, y),
        'right_ear': (x, y), 'left_shoulder': (x, y), 'right_shoulder': (x, y),
        'left_hip': (x, y), 'right_hip': (x, y)
      }
    """
    # Preprocess the image
    height, width, _ = image.shape
    #print(f"Original image size: {width}x{height}")

    input_image, scale, pad_h, pad_w = resize_with_padding(image, 192)
    input_image = tf.cast(input_image, dtype=tf.int32)[tf.newaxis, ...]

    # Get PoseNet keypoints
    results = posenet_model(input_image)
    keypoints_with_scores = results['output_0'].numpy()

    # Extract keypoints
    keypoints = keypoints_with_scores[0, 0, :, :2]
    scores = keypoints_with_scores[0, 0, :, 2]

    # Reverse scaling and padding
    keypoints[:, 0] = (keypoints[:, 0] * 192 - pad_h) / scale
    keypoints[:, 1] = (keypoints[:, 1] * 192 - pad_w) / scale

    # Initialize dictionary to hold scaled keypoints
    keypoints_scaled = {}

    for name, idx in keypoint_indices.items():
        if name in ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']:
            x_scaled = keypoints[idx][1] / width  # Adjust for original image width
            y_scaled = keypoints[idx][0] / height  # Adjust for original image height
            keypoints_scaled[name] = (x_scaled, y_scaled)
            #print(f"{name}: Scaled to original image -> ({x_scaled}, {y_scaled})")

    return keypoints_scaled

def calculate_average_angle(keypoints_scaled):
    """
    Calculate the average angle between specified keypoints.

    Args:
    - keypoints_scaled (dict): Scaled keypoints with their coordinates.

    Returns:
    - float: The average angle.
    """
    angles = []
    
    def angle_between(p1, p2):
        return np.arctan2(p2[1] - p1[1], p2[0] - p1[0])

    if 'left_shoulder' in keypoints_scaled and 'right_shoulder' in keypoints_scaled:
        angles.append(angle_between(keypoints_scaled['left_shoulder'], keypoints_scaled['right_shoulder']))
    
    if 'left_hip' in keypoints_scaled and 'right_hip' in keypoints_scaled:
        angles.append(angle_between(keypoints_scaled['left_hip'], keypoints_scaled['right_hip']))
    
    if 'left_eye' in keypoints_scaled and 'right_eye' in keypoints_scaled:
        angles.append(angle_between(keypoints_scaled['left_eye'], keypoints_scaled['right_eye']))
    
    if 'left_ear' in keypoints_scaled and 'right_ear' in keypoints_scaled:
        angles.append(angle_between(keypoints_scaled['left_ear'], keypoints_scaled['right_ear']))

    if angles:
        average_angle = np.mean(angles)
        #print("Calculated Angles:", angles)
        #print("Average Angle:", average_angle)
        return average_angle
    else:
        #print("No angles calculated.")
        return None

import numpy as np

def prepare_feature_vector(image, box_coords, posenet_model, depth_value):
    """
    Prepare the feature vector for a person detected in an image, ready for model prediction.

    Args:
    - image (numpy array): The original image containing the detected person.
    - box_coords (tuple): The bounding box coordinates of the detected person (x1, y1, x2, y2).
    - posenet_model: The pre-trained PoseNet model for keypoint extraction.
    - depth_value (float): The depth value estimated for the person detected.

    Returns:
    - feature_vector (numpy array): The feature vector ready to be input into the model.
    """
    x1, y1, x2, y2 = box_coords

    # Crop the image to the bounding box
    cropped_image = image[y1:y2, x1:x2]

    # Resize the cropped image to the input size expected by PoseNet
    resized_image = resize_to_x_by_x(cropped_image, (192, 192))
    
    # Extract and scale keypoints from the resized cropped image
    keypoints_scaled = extract_and_scale_keypoints(resized_image, posenet_model)

    # Replace missing keypoints with -1
    keypoints_scaled = {k: (round(v[0], 2), round(v[1], 2)) if v != (-1, -1) else (-1, -1) for k, v in keypoints_scaled.items()}

    # Extract the values from the dictionary to form a list
    keypoints_list = list(keypoints_scaled.values())

    # Flatten the list of tuples to a single list of coordinates
    keypoints_flat = [coord for point in keypoints_list for coord in (point if point != (-1, -1) else [-1, -1])]

    # Replace any NaN values with -1
    keypoints_flat = [-1 if np.isnan(coord) else coord for coord in keypoints_flat]

    # Calculate the average angle
    average_angle = calculate_average_angle(keypoints_scaled)
    if average_angle is not None:
        average_angle = round(average_angle, 2)
    else:
        average_angle = -1

    # Use the depth value provided
    distance = depth_value

    # Create the feature vector and ensure it's a flat array
    feature_vector = keypoints_flat + [average_angle, distance]

    # Convert to a numpy array for model input
    feature_vector = np.array(feature_vector, dtype=np.float64).reshape(1, -1)

    return feature_vector