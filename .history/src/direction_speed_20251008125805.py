"""
direction_speed.py
Contains functions to calculate the direction and speed of detected persons.
"""

import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
from src.utils import resize_with_padding, display_img

# Dictionary of keypoint indices
keypoint_indices = {
    'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
    'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
    'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
    'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
}

def calculate_keypoint_direction(keypoint_coords):
    """
    Calculates the direction based on keypoint coordinates.

    Args:
    - keypoint_coords (dict): Dictionary containing detected keypoints and their coordinates.

    Returns:
    - angle (float): Calculated angle in radians.
    """
    vectors = []

    # Prioritize head keypoints for direction calculation
    head_keypoints = ['left_eye', 'right_eye', 'nose']
    if all(k in keypoint_coords for k in head_keypoints):
        left_eye = keypoint_coords['left_eye']
        right_eye = keypoint_coords['right_eye']
        nose = keypoint_coords['nose']

        # Vector between left and right eyes
        eye_vector = np.array(right_eye) - np.array(left_eye)
        # Vector from the midpoint of the eyes to the nose
        nose_to_eye_vector = np.array(nose) - np.array((np.array(left_eye) + np.array(right_eye)) / 2)
        
        vectors.append(eye_vector)
        vectors.append(nose_to_eye_vector)
    else:
        # Fallback to body keypoints if head keypoints are not available
        if 'left_hip' in keypoint_coords and 'right_hip' in keypoint_coords:
            left_hip = keypoint_coords['left_hip']
            right_hip = keypoint_coords['right_hip']
            hip_vector = np.array(right_hip) - np.array(left_hip)
            vectors.append(hip_vector)

        if 'left_shoulder' in keypoint_coords and 'right_shoulder' in keypoint_coords:
            left_shoulder = keypoint_coords['left_shoulder']
            right_shoulder = keypoint_coords['right_shoulder']
            shoulder_vector = np.array(right_shoulder) - np.array(left_shoulder)
            vectors.append(shoulder_vector)

        if 'left_eye' in keypoint_coords and 'right_eye' in keypoint_coords:
            left_eye = keypoint_coords['left_eye']
            right_eye = keypoint_coords['right_eye']
            eye_vector = np.array(right_eye) - np.array(left_eye)
            vectors.append(eye_vector)

    # Calculate mean vector and determine angle
    if vectors:
        mean_vector = np.mean(vectors, axis=0)
        angle = np.arctan2(mean_vector[1], mean_vector[0])

        # Ensure angle is within the range [0, 2*pi]
        if angle < 0:
            angle += 2 * np.pi

        return angle

    return None


def calculate_direction(frame, box_coords, depth_values, posenet_model, DISP=True):
    """
    NOT USED ANYMORE BCS WE HAVE OUR OWN SVM MODEL
    Calculates the direction and speed of detected persons.

    Args:
    - frame (numpy array): The input image array.
    - box_coords (list of tuples): List of coordinates for the bounding boxes.
    - depth_values (list of floats): List of predicted depths.
    - posenet_model (model): PoseNet model for keypoint detection.
    - DISP (bool): Display flag (True to display, False to not display).

    Returns:
    - directions (list of floats): List of head directions for each person, in radians.
    """
    directions = []
    box_idx = 0

    for box in box_coords:
        if depth_values[box_idx] < 6:
            x1, y1, x2, y2 = map(int, box)
            if DISP:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cropped_frame = frame[y1:y2, x1:x2]
            input_image, scale, pad_h, pad_w = resize_with_padding(cropped_frame, 192)
            input_image = tf.cast(input_image, dtype=tf.int32)[tf.newaxis, ...]

            results = posenet_model(input_image)
            keypoints_with_scores = results['output_0'].numpy()

            keypoints = keypoints_with_scores[0, 0, :, :2]
            scores = keypoints_with_scores[0, 0, :, 2]

            # Apply inverse scaling and padding
            keypoints[:, 0] = (keypoints[:, 0] * 192 - pad_h) / scale
            keypoints[:, 1] = (keypoints[:, 1] * 192 - pad_w) / scale

            # Adjust keypoints relative to the box coordinates
            keypoints[:, 0] += y1
            keypoints[:, 1] += x1

            keypoint_coords = {}
            for name, idx in keypoint_indices.items():
                y, x = keypoints[idx]
                if scores[idx] > 0.2:  # Only display keypoints with sufficient confidence
                    if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                        x, y = int(x), int(y)
                        keypoint_coords[name] = (x, y)
                        if DISP:
                            cv2.circle(frame, (x, y), 3 , (0, 0, 255), -1)
                            cv2.putText(frame, name, (x + 10, y), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            angle = calculate_keypoint_direction(keypoint_coords)

            if angle is not None:
                if DISP:
                    nose_x, nose_y = keypoint_coords.get('nose', (0, 0))
                    x_center, y_center = int((x1 + x2) / 2), int((y1 + y2) / 2)
                    arrow_length = 50

                    if nose_x != 0 and nose_y != 0:
                        end_x = int(nose_x - arrow_length * np.cos(angle))
                        end_y = int(nose_y - arrow_length * np.sin(angle))

                        cv2.arrowedLine(frame, (nose_x, nose_y), (end_x, end_y), (255, 0, 0), 3)
                    else:
                        end_x = int(x_center - arrow_length * np.cos(angle))
                        end_y = int(y_center - arrow_length * np.sin(angle))

                        cv2.arrowedLine(frame, (x_center, y_center), (end_x, end_y), (255, 0, 0), 2)
                        cv2.putText(frame, f'Angle: {angle:.2f} rad', (x_center, y_center - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1, 1, 2155), 2, cv2.LINE_AA)

                directions.append(angle)
        box_idx += 1

    print('Direction estimation complete')
    if DISP:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_img(frame_rgb, title="Human Detection and Pose Estimation")
    return directions

def calculate_speed(frame, box_coords, previous_positions=None):
    """
    Calculate the speed of detected persons based on their movement between frames.
    
    Args:
    - frame (numpy array): Current frame
    - box_coords (list of tuples): Current bounding box coordinates
    - previous_positions (list of tuples, optional): Previous frame positions for speed calculation
    
    Returns:
    - speeds (list of floats): Calculated speeds for each person
    """
    speeds = []
    
    if previous_positions is None or len(previous_positions) != len(box_coords):
        # If no previous positions, return default speed
        for i in range(len(box_coords)):
            speeds.append(1.0)  # Default speed in m/s
        return speeds
    
    for i, (current_box, prev_pos) in enumerate(zip(box_coords, previous_positions)):
        try:
            # Calculate center of current bounding box
            x1, y1, x2, y2 = current_box
            current_center = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            # Calculate distance moved
            distance = np.sqrt((current_center[0] - prev_pos[0])**2 + (current_center[1] - prev_pos[1])**2)
            
            # Convert pixels to meters (assuming 1 pixel = 0.001 meters)
            distance_meters = distance * 0.001
            
            # Calculate speed (assuming 30 FPS)
            speed = distance_meters * 30  # m/s
            
            # Cap the speed to reasonable limits
            speed = max(0.1, min(speed, 5.0))  # Between 0.1 and 5.0 m/s
            
            speeds.append(speed)
            
        except Exception as e:
            print(f"Error calculating speed for person {i}: {e}")
            speeds.append(1.0)  # Default speed on error
    
    return speeds