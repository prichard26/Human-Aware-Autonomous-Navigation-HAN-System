"""
calibration.py
Contains functions for calibrating the depth estimation model using known distances.
"""
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from src.depth_estimation import estimate_depth
from src.draw_boxes import draw_boxes, detect_persons, find_closest_person
from src.utils import preprocess_boxes, calculate_pixel_value, combine_and_save_images, rational_func, exponential_func, power_law_func

def process_and_plot_calibration(base_path, yolo_model, depth_processor, depth_model, output_path=None):
    """
    Processes all images for calibration, calculates depths, and plots the relationship between average depth and actual distance.
    Evaluates multiple regression models and determines the best one.
    
    Args:
    - base_path (str): The file path to the directory containing the calibration images.
    - yolo_model (model): YOLO model for person detection.
    - output_path (str, optional): The file path to the directory to save the combined images. If None, images are not saved.
    
    Returns:
    - best_model (str): The name of the best regression model.
    - best_params (tuple): Parameters of the best regression model.
    """
    distances = []  # List to store actual distances
    avg_depths = []  # List to store average depths
    
    for filename in os.listdir(base_path):
        if filename.endswith(".jpeg"):
            try:
                # Extract distance from filename
                distance_str = filename.split('.')[0] + '.' + filename.split('.')[1]
                distance = float(distance_str)
                distances.append(distance)
                print(f"Filename: {filename}, Extracted Distance: {distance}")

                image_path = os.path.join(base_path, filename)
                print(f"Processing image: {image_path}")

                # Use cv2 to read the image
                image = cv2.imread(image_path)
                if image is None:
                    raise FileNotFoundError(f"Image not found at {image_path}")

                depth_image = estimate_depth(image, depth_processor, depth_model)
                coords = detect_persons(image, yolo_model)
                filtered_depth_images = preprocess_boxes(depth_image, coords)
                depths = calculate_pixel_value(filtered_depth_images)

                closest_coord, closest_depth = find_closest_person(depths, coords)
                avg_depths.append(closest_depth)

                if output_path:
                    boxed_image = draw_boxes(image, [closest_coord])
                    combined_output_path = os.path.join(output_path, f"combined_{filename}")
                    combine_and_save_images(depth_image, boxed_image, combined_output_path)
            except FileNotFoundError:
                print(f"Image not found: {image_path}")
            except Exception as e:
                print(f"An error occurred while processing {image_path}: {str(e)}")

    avg_depths = np.array(avg_depths)  # Convert to NumPy array for fitting functions

    if len(avg_depths) == 0 or len(distances) == 0:
        print("No data to plot or fit. Ensure that the calibration images are correctly processed.")
        return None, None

    if len(avg_depths) != len(distances):
        raise ValueError("The number of depth measurements does not match the number of distances.")

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # Plot the original data
    axes[0].scatter(avg_depths, distances, c=distances, cmap='plasma')
    axes[0].set_xlabel('Average Depth (pixel value btw [0, 255])')
    axes[0].set_ylabel('Actual Distance (meters)')
    axes[0].set_title('Original Data')
    axes[0].grid(True)

    # Fit models
    poly_coeff = np.polyfit(avg_depths, distances, 2)
    poly_model = np.poly1d(poly_coeff)
    exp_popt, _ = curve_fit(exponential_func, avg_depths, distances, p0=(1, -0.01, 1), maxfev=100000)
    power_popt, _ = curve_fit(power_law_func, avg_depths, distances, p0=(1, -1), maxfev=100000)
    rational_popt, _ = curve_fit(rational_func, avg_depths, distances, p0=(1, 1, 0), maxfev=100000)

    # Plot all fits
    avg_depths_range = np.linspace(min(avg_depths), max(avg_depths), 100)
    axes[1].scatter(avg_depths, distances, c=distances, cmap='plasma')
    axes[1].plot(avg_depths_range, poly_model(avg_depths_range), color='blue', label='Polynomial Fit')
    axes[1].plot(avg_depths_range, exponential_func(avg_depths_range, *exp_popt), color='red', label='Exponential Fit')
    axes[1].plot(avg_depths_range, power_law_func(avg_depths_range, *power_popt), color='green', label='Power-Law Fit')
    axes[1].plot(avg_depths_range, rational_func(avg_depths_range, *rational_popt), color='purple', label='Rational Fit')
    axes[1].set_xlabel('Average Depth (pixel value btw [0, 255])')
    axes[1].set_ylabel('Actual Distance (meters)')
    axes[1].set_title('All Fits')
    axes[1].legend()
    axes[1].grid(True)

    # Determine best fit
    poly_pred = poly_model(avg_depths)
    exp_pred = exponential_func(avg_depths, *exp_popt)
    power_pred = power_law_func(avg_depths, *power_popt)
    rational_pred = rational_func(avg_depths, *rational_popt)

    poly_error = np.mean(np.abs(distances - poly_pred))
    exp_error = np.mean(np.abs(distances - exp_pred))
    power_error = np.mean(np.abs(distances - power_pred))
    rational_error = np.mean(np.abs(distances - rational_pred))

    errors = {
        'Polynomial': poly_error,
        'Exponential': exp_error,
        'Power-Law': power_error,
        'Rational': rational_error
    }

    best_model = min(errors, key=errors.get)
    best_params = {
        'Polynomial': poly_coeff,
        'Exponential': exp_popt,
        'Power-Law': power_popt,
        'Rational': rational_popt
    }[best_model]

    # Plot best fit
    axes[2].scatter(avg_depths, distances, c=distances, cmap='plasma')
    if best_model == 'Polynomial':
        best_fit = poly_model(avg_depths_range)
        best_equation = f"y = {poly_coeff[0]:.4f}x^2 + {poly_coeff[1]:.4f}x + {poly_coeff[2]:.4f}"
    elif best_model == 'Exponential':
        best_fit = exponential_func(avg_depths_range, *exp_popt)
        best_equation = f"y = {exp_popt[0]:.4f} * exp({exp_popt[1]:.4f} * x) + {exp_popt[2]:.4f}"
    elif best_model == 'Power-Law':
        best_fit = power_law_func(avg_depths_range, *power_popt)
        best_equation = f"y = {power_popt[0]:.4f} * x^{power_popt[1]:.4f}"
    elif best_model == 'Rational':
        best_fit = rational_func(avg_depths_range, *rational_popt)
        best_equation = f"y = {rational_popt[0]:.4f} / (x + {rational_popt[1]:.4f}) + {rational_popt[2]:.4f}"
    axes[2].plot(avg_depths_range, best_fit, label=f'Best Fit ({best_model})')
    axes[2].set_xlabel('Average Depth (pixel value btw [0, 255])')
    axes[2].set_ylabel('Actual Distance (meters)')
    axes[2].set_title(f'Best Fit: {best_model}')
    axes[2].legend()
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Best model: {best_model} with error {errors[best_model]:.4f} and equation: {best_equation}")

    return best_model, best_params
