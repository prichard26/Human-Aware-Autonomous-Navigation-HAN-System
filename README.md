
# CV_PROJECT

This project implements a sophisticated computer vision-based system designed for human detection, depth estimation, direction and speed calculation, and autonomous navigation within dynamic environments. The system integrates cutting-edge machine learning models and computer vision techniques to enable human-aware path planning and navigation.

## Project Structure

- **`data/`**: Directory for input and output data files.
- **`models/`**: Directory containing pre-trained models used for various detection and estimation tasks.
- **`notebooks/`**: Contains Jupyter notebooks for experimentation, prototyping, and visualizing results.
- **`src/`**: Source code directory, organized into key modules:
  - `calibration.py`: Functions for camera and sensor calibration to ensure accurate depth and spatial measurements.
  - `draw_boxes.py`: Utilities for drawing bounding boxes around detected objects, primarily humans.
  - `depth_estimation.py`: Methods and algorithms for estimating depth from camera images, crucial for understanding the 3D environment.
  - `cost_map.py`: Functions to generate cost maps, used in path planning to navigate efficiently and avoid obstacles.
  - `direction_speed.py`: Functions to calculate the direction and speed of detected humans, aiding in dynamic path planning.
  - `navigation_algo.py`: Core navigation algorithm that integrates detection, estimation, and planning to guide the robot.
  - `utils.py`: General utility functions used across different modules, including image preprocessing and mathematical operations.
  - `__init__.py`: Initializes the `src` package, allowing its modules to be imported elsewhere in the project.
  
- `config.py`: Configuration file containing various settings and parameters used throughout the project.
- `environment.yml`: Conda environment specification file, listing all dependencies required to run the project.
- `main.py`: The main entry point for running the project, orchestrating the various modules for a cohesive system execution.

## Setup

To get started with this project, follow these steps:

1. **Create a Conda environment and install dependencies**:

   Open your terminal and execute the following commands:

   ```bash
   conda env create -f environment.yml
   conda activate cv_project
   ```

   This will create a new Conda environment named `cv_project` with all the necessary dependencies installed.

2. **Configure the Project**:

   Ensure that all paths in `config.py` are correctly set to match your environment, especially if you're using custom data paths or models.

3. **Run the Project**:

   Once everything is set up, you can start the project by running:

   ```bash
   python main.py
   ```

   This will initiate the system, integrating human detection, depth estimation, and navigation algorithms to operate effectively in a dynamic environment.
