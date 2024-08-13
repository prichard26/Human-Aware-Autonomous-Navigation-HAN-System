"""
draw_boxes.py
Contains functions for drawing bounding boxes around detected persons in an image. Along with functions related to detecting persons in an image using the YOLO model.
"""

import cv2
import numpy as np

def draw_boxes(image, coords):
    """
    Draws bounding boxes around detected persons in the image.
    
    Args:
    - image_path (str): The file path to the input image.
    - coords (list of tuples): List of coordinates for the bounding boxes.
    
    Returns:
    - image_rgb (numpy array): Image with bounding boxes drawn.
    """
    for idx, (x1, y1, x2, y2) in enumerate(coords):
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f'{idx+1}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)
        x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
        cv2.circle(image, (x_center, y_center), 5, (0, 0, 255), -1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb


def detect_persons(image, yolo_model):
    """
    Detects persons in the image using the YOLO model.

    Args:
    - image_path (str): The file path to the input image.
    - yolo_model: The pre-trained YOLO model.

    Returns:
    - coords (list of tuples): List of coordinates for detected persons.
    """
    results = yolo_model(image)
    df = results.pandas().xyxy[0]
    persons = df[df['name'] == 'person']
    coords = []
    for _, row in persons.iterrows():
        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        coords.append((x1, y1, x2, y2))
    
    print(f"Person detection complete. Found {len(coords)} persons.")
    return coords

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
    closest_idx = np.argmax(depths)
    closest_coord = coords[closest_idx]
    return closest_coord, depths[closest_idx]
