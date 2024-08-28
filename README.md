# Human-Aware Autonomous Navigation (HAAN) System

## Overview

The Human-Aware Autonomous Navigation (HAAN) System is a sophisticated framework designed to enable a robot to navigate safely and efficiently in dynamic environments populated by humans. The system uses a combination of computer vision, depth estimation, and probabilistic A* path planning to predict human movements and avoid collisions.

## Key Features

- **Real-time Path Planning**: Uses probabilistic A* algorithm for efficient and safe path planning in dynamic environments.
- **Human Detection and Tracking**: Utilizes YOLO for person detection and PoseNet for keypoint detection to predict human movements.
- **Depth Estimation**: Integrates depth estimation techniques to measure the distance of humans from the robot.
- **Direction and Speed Estimation**: Estimates the direction and speed of detected humans to predict their future positions.
- **Simulation Environment**: Includes a simulation module for testing and visualizing the robot's navigation in a dynamic environment.

## Installation

To set up the HAAN system, follow these steps:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/prichard26/Human-Aware-Autonomous-Navigation-HAN-System.git
    ```

2. **Navigate to the project directory**:

    ```bash
    cd Human-Aware-Autonomous-Navigation-HAN-System
    ```

3. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Directory Structure

The project has the following structure:

```plaintext
.
├── data/                        # Directory containing data files
├── images/                      # Directory containing images used in the project
├── model/                       # Directory containing model files
│   └── orientation_model.pkl    # Pre-trained orientation model
├── src/                         # Source code directory
│   ├── __init__.py              # Init file for the src package
│   ├── calibration.py           # Calibration module for the camera system
│   ├── depth_estimation.py      # Module for depth estimation from images
│   ├── direction_speed.py       # Module for direction and speed estimation of detected persons
│   ├── draw_boxes.py            # Utility to draw bounding boxes around detected persons
│   ├── model_initialization.py  # Module to initialize and load the ML models
│   ├── simulation_a_star.py     # A* algorithm for path planning
│   ├── simulation_a_star_futur.py # Extended A* algorithm for future enhancements
│   └── utils.py                 # Utility functions used across the project
├── testing/                     # Directory for testing files and scripts
├── main.ipynb                   # Main Jupyter notebook for running the system
├── CV_PROJECT.ipynb             # Additional Jupyter notebook for computer vision tasks
├── LICENSE                      # License file
├── README.md                    # Project documentation
└── environment.yml              # Conda environment configuration file

## Pipeline

The HAAN System follows a well-structured pipeline:

### 1. **Person Detection**
   - **Module**: `model_initialization.py`, `draw_boxes.py`
   - **Description**: Detects humans in the camera feed using YOLO and marks them with bounding boxes.

### 2. **Depth Estimation**
   - **Module**: `depth_estimation.py`
   - **Description**: Estimates the depth (distance) of each detected person from the robot using a pre-trained depth model.

### 3. **Direction and Speed Estimation**
   - **Module**: `direction_speed.py`
   - **Description**: Estimates the direction and speed of each detected person by analyzing their movement and orientation.

### 4. **Path Planning**
   - **Module**: `simulation_a_star.py`
   - **Description**: Computes the safest and most efficient path for the robot to navigate through the dynamic environment using a probabilistic A* algorithm.

### 5. **Simulation and Visualization**
   - **Module**: `main.ipynb`
   - **Description**: Simulates the robot's movement, displays the dynamic obstacles, and visualizes the planned path.

## How to Run

1. **Calibration**: 
   - Run `calibration.py` to calibrate your camera system.
   
2. **Person Detection and Depth Estimation**: 
   - Use the notebook `main.ipynb` to detect persons, estimate their depth, and visualize the bounding boxes.

3. **Direction and Speed Estimation**: 
   - The module `direction_speed.py` can be run to estimate the movement patterns of the detected persons.

4. **Path Planning and Simulation**: 
   - The `simulation_a_star.py` script runs the probabilistic A* algorithm and simulates the robot's movement.

5. **Visualization**: 
   - Use the functions in `utils.py` and `main.ipynb` to visualize the robot's navigation, obstacles, and paths.

## Example Results

**Image 1**: Person Detection with Bounding Boxes

**Image 2**: Depth Estimation Results

**GIF**: Robot Navigation through Dynamic Environment

## Requirements

- Python 3.8+
- OpenCV
- TensorFlow
- Matplotlib
- NumPy
- SciPy

## Future Work

- Implement more advanced human motion prediction models.
- Integrate additional sensors for improved environment perception.
- Expand the system for outdoor navigation in more complex environments.