#!/usr/bin/env python3
"""
Enhanced main script for the HAAN system with improved error handling,
performance monitoring, and debugging capabilities.
"""

import sys
import os
import time
import traceback
from typing import Optional, Tuple, List
import numpy as np
import cv2
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import preprocess_boxes, calculate_pixel_value, horizontal_pixel_pos, horizontal_pos_conversion, predict_distance, get_image_size, resize_to_x_by_x, prepare_feature_vector
from src.model_initialization import load_yolo_model, load_posenet_model, load_depth_estimation_model, load_orientation_model, load_depth_curve_spec
from src.simulation_a_star import simulation, animate_cost_map, create_internal_obstacles
from src.direction_speed import calculate_speed
from src.depth_estimation import estimate_depth
from src.draw_boxes import detect_persons
from src.debug_utils import PerformanceMonitor, DebugVisualizer, ErrorHandler, performance_monitor, error_handler

class HAANSystem:
    """Enhanced HAAN system with improved error handling and monitoring."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the HAAN system with optional configuration."""
        self.config = config or self._get_default_config()
        self.models = {}
        self.previous_positions = []
        self.performance_monitor = performance_monitor
        self.error_handler = error_handler
        self.debug_visualizer = DebugVisualizer()
        
        # Initialize models
        self._load_models()
        
    def _get_default_config(self) -> dict:
        """Get default configuration parameters."""
        return {
            'scale': 0.3,
            'robot_speed': 1.11 * 0.3,
            'new_size': (1280, 1280),
            'start': (0, 0),
            'goal': (-20 * 0.3, 900 * 0.3),
            'simulation_time': 100000,
            'dt': 100,
            'grid_size': (1280, 1000),
            'display_results': True,
            'save_debug_images': True,
            'debug_output_dir': 'debug_output'
        }
    
    def _load_models(self):
        """Load all required models with error handling."""
        try:
            print("Loading AI models...")
            self.models['yolo'] = load_yolo_model()
            self.models['posenet'] = load_posenet_model()
            self.models['orientation'] = load_orientation_model()
            self.models['depth_processor'], self.models['depth_model'] = load_depth_estimation_model()
            self.models['depth_curve_type'], self.models['depth_curve_params'] = load_depth_curve_spec()
            print("✅ All models loaded successfully!")
            
        except Exception as e:
            self.error_handler.handle_detection_error(e, "Model loading")
            print(f"❌ Error loading models: {e}")
            raise
    
    def process_image(self, image_path: str) -> dict:
        """Process a single image with enhanced error handling."""
        try:
            self.performance_monitor.start_monitoring()
            
            # Load and preprocess image
            img, size_img = get_image_size(image_path)
            resized_image = resize_to_x_by_x(img, self.config['new_size'])
            
            # Person detection
            coords_box_in_pixel = detect_persons(resized_image, self.models['yolo'])
            print(f"Detected {len(coords_box_in_pixel)} persons")
            
            if len(coords_box_in_pixel) == 0:
                print("⚠️ No persons detected in the image")
                return {'error': 'No persons detected'}
            
            # Depth estimation
            depth_image = estimate_depth(resized_image, self.models['depth_processor'], self.models['depth_model'])
            box_without_background = preprocess_boxes(depth_image, coords_box_in_pixel)
            mean_pixel_values = calculate_pixel_value(box_without_background)
            depth_values = [predict_distance(pv, self.models['depth_curve_params'], 
                                           self.models['depth_curve_type'].lower()) 
                          for pv in mean_pixel_values]
            
            # Horizontal position estimation
            horizontal_pos_in_pixel = horizontal_pixel_pos(coords_box_in_pixel)
            horizontal_pos_in_cm = horizontal_pos_conversion(horizontal_pos_in_pixel)
            
            # Direction and speed estimation
            features_vector = [prepare_feature_vector(resized_image, box, self.models['posenet'], depth) 
                            for box, depth in zip(coords_box_in_pixel, depth_values)]
            directions = [self.models['orientation'].predict(features) for features in features_vector]
            directions_in_radians = [np.radians(direction[0]) for direction in directions]
            speeds = calculate_speed(resized_image, coords_box_in_pixel, self.previous_positions)
            
            # Update previous positions for next frame
            self.previous_positions = [((x1+x2)/2, (y1+y2)/2) for x1, y1, x2, y2 in coords_box_in_pixel]
            
            # Record performance metrics
            self.performance_monitor.record_metrics(
                detection_count=len(coords_box_in_pixel),
                path_length=None
            )
            
            # Create obstacles for simulation
            num_obstacles = len(coords_box_in_pixel)
            dynamic_obstacles_pos = np.zeros((num_obstacles, 2))
            dynamic_obstacles_dir_speed = []
            
            for i, (horizontal_pos, depth, direction, speed) in enumerate(zip(horizontal_pos_in_cm, depth_values, directions_in_radians, speeds)):
                x_position = int(horizontal_pos * self.config['scale'])
                y_position = int(depth * self.config['scale'])
                
                dynamic_obstacles_pos[i, :] = [x_position, y_position]
                dynamic_obstacles_dir_speed.append((direction, speed))
            
            result = {
                'success': True,
                'obstacles_pos': dynamic_obstacles_pos,
                'obstacles_dir_speed': dynamic_obstacles_dir_speed,
                'detections': coords_box_in_pixel,
                'depths': depth_values,
                'directions': directions_in_radians,
                'speeds': speeds,
                'image': resized_image
            }
            
            # Debug visualization
            if self.config['save_debug_images']:
                self._save_debug_visualization(result, image_path)
            
            return result
            
        except Exception as e:
            self.error_handler.handle_detection_error(e, f"Processing image {image_path}")
            self.performance_monitor.increment_error_count()
            print(f"❌ Error processing image: {e}")
            traceback.print_exc()
            return {'error': str(e)}
    
    def run_simulation(self, obstacles_pos: np.ndarray, obstacles_dir_speed: List, 
                      use_internal_obstacles: bool = False, num_internal_obstacles: int = 20) -> dict:
        """Run the simulation with enhanced error handling."""
        try:
            if use_internal_obstacles:
                obstacles_pos, obstacles_dir_speed = create_internal_obstacles(num_internal_obstacles)
                print(f"Using {num_internal_obstacles} internal obstacles")
            
            print("Starting simulation...")
            start_time = time.time()
            
            robot_positions, cost_map_times, dynamic_obstacles_times, path_times, dynamic_obstacles_dir_speed_times = simulation(
                obstacles_pos,
                obstacles_dir_speed,
                self.config['start'],
                self.config['goal'],
                self.config['robot_speed'],
                self.config['simulation_time'],
                self.config['dt']
            )
            
            simulation_time = time.time() - start_time
            print(f"✅ Simulation completed in {simulation_time:.2f} seconds")
            
            # Record performance metrics
            self.performance_monitor.record_metrics(
                detection_count=len(obstacles_pos),
                path_length=len(robot_positions) if robot_positions else 0
            )
            
            result = {
                'success': True,
                'robot_positions': robot_positions,
                'cost_map_times': cost_map_times,
                'dynamic_obstacles_times': dynamic_obstacles_times,
                'path_times': path_times,
                'dynamic_obstacles_dir_speed_times': dynamic_obstacles_dir_speed_times,
                'simulation_time': simulation_time
            }
            
            return result
            
        except Exception as e:
            self.error_handler.handle_pathfinding_error(e, "Simulation execution")
            self.performance_monitor.increment_error_count()
            print(f"❌ Error running simulation: {e}")
            traceback.print_exc()
            return {'error': str(e)}
    
    def create_animation(self, simulation_result: dict, save_path: Optional[str] = None) -> Optional[object]:
        """Create animation from simulation results."""
        try:
            if not simulation_result.get('success', False):
                print("❌ Cannot create animation: simulation failed")
                return None
            
            print("Creating animation...")
            anim = animate_cost_map(
                simulation_result['cost_map_times'],
                simulation_result['robot_positions'],
                simulation_result['dynamic_obstacles_times'],
                simulation_result['dynamic_obstacles_dir_speed_times'],
                self.config['goal'],
                self.config['simulation_time'],
                self.config['dt'],
                simulation_result['path_times']
            )
            
            if save_path:
                print(f"Saving animation to {save_path}")
                # Note: Animation saving would require additional setup
            
            return anim
            
        except Exception as e:
            self.error_handler.handle_pathfinding_error(e, "Animation creation")
            print(f"❌ Error creating animation: {e}")
            return None
    
    def _save_debug_visualization(self, result: dict, image_path: str):
        """Save debug visualization images."""
        try:
            debug_dir = Path(self.config['debug_output_dir'])
            debug_dir.mkdir(exist_ok=True)
            
            image_name = Path(image_path).stem
            save_path = debug_dir / f"{image_name}_debug.png"
            
            self.debug_visualizer.visualize_detection_results(
                result['image'],
                result['detections'],
                result['depths'],
                result['directions'],
                result['speeds'],
                str(save_path)
            )
            
        except Exception as e:
            print(f"Warning: Could not save debug visualization: {e}")
    
    def get_system_status(self) -> dict:
        """Get current system status and performance metrics."""
        return {
            'performance': self.performance_monitor.get_performance_summary(),
            'errors': self.error_handler.get_error_summary(),
            'config': self.config
        }
    
    def save_performance_report(self, output_path: str = "performance_report.png"):
        """Save performance monitoring report."""
        try:
            self.performance_monitor.plot_performance(output_path)
            print(f"Performance report saved to {output_path}")
        except Exception as e:
            print(f"Error saving performance report: {e}")

def main():
    """Main function to run the enhanced HAAN system."""
    print("🤖 HAAN System - Enhanced Version")
    print("=" * 50)
    
    # Initialize system
    haan = HAANSystem()
    
    # Example usage
    try:
        # Process an image
        image_path = "/Users/paulrichard/Documents/Infosys/HAAN/data/input/random_test/IMG_2339.jpeg"
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            print("Please provide a valid image path")
            return
        
        print(f"Processing image: {image_path}")
        result = haan.process_image(image_path)
        
        if result.get('success', False):
            print("✅ Image processing successful!")
            
            # Run simulation
            simulation_result = haan.run_simulation(
                result['obstacles_pos'],
                result['obstacles_dir_speed'],
                use_internal_obstacles=True,
                num_internal_obstacles=20
            )
            
            if simulation_result.get('success', False):
                print("✅ Simulation completed successfully!")
                
                # Create animation
                anim = haan.create_animation(simulation_result)
                if anim:
                    print("✅ Animation created successfully!")
            
            # Save performance report
            haan.save_performance_report()
            
        else:
            print(f"❌ Image processing failed: {result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        # Print final status
        status = haan.get_system_status()
        print("\n📊 Final System Status:")
        print(f"Performance: {status['performance']}")
        print(f"Errors: {status['errors']}")

if __name__ == "__main__":
    main()
