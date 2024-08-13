# CV_PROJECT

This project implements a computer vision-based system for human detection, depth estimation, direction and speed calculation, and navigation in a dynamic environment.

## Project Structure

- `data/`: Contains input and output data.
- `models/`: Contains pre-trained models.
- `notebooks/`: Contains Jupyter notebooks for experimentation.
- `src/`: Contains source code.
  - `calibration.py`: Calibration functions.
  - `draw_boxes.py`: Functions for drawing bounding boxes.
  - `depth_estimation.py`: Functions for depth estimation.
  - `keypoints.py`: Functions for keypoint detection.
  - `cost_map.py`: Functions for creating cost maps.
  - `direction_speed.py`: Functions for calculating direction and speed.
  - `navigation_algo.py`: Navigation algorithm.
  - `utils.py`: Utility functions.
- `config.py`: Configuration settings.
- `environment.yml`: Conda environment specification.
- `main.py`: Main entry point for the project.

## Setup

1. Create a conda environment and install dependencies:

```bash
conda env create -f environment.yml
conda activate cv_project
