"""
debug_utils.py
Enhanced debugging and performance monitoring utilities for the HAAN system.
"""

import time
import psutil
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Data class to store performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    execution_time: float
    frame_count: int
    detection_count: int
    path_length: Optional[int] = None
    error_count: int = 0

class PerformanceMonitor:
    """Monitor and track system performance metrics."""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.start_time = None
        self.frame_count = 0
        self.error_count = 0
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.frame_count = 0
        self.error_count = 0
        logger.info("Performance monitoring started")
        
    def record_metrics(self, detection_count: int = 0, path_length: Optional[int] = None):
        """Record current performance metrics."""
        if self.start_time is None:
            logger.warning("Monitoring not started. Call start_monitoring() first.")
            return
            
        current_time = time.time()
        execution_time = current_time - self.start_time
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            execution_time=execution_time,
            frame_count=self.frame_count,
            detection_count=detection_count,
            path_length=path_length,
            error_count=self.error_count
        )
        
        self.metrics_history.append(metrics)
        self.frame_count += 1
        
        # Log performance warnings
        if metrics.cpu_percent > 80:
            logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        if metrics.memory_percent > 80:
            logger.warning(f"High memory usage: {metrics.memory_percent:.1f}%")
            
    def increment_error_count(self):
        """Increment the error counter."""
        self.error_count += 1
        logger.warning(f"Error count increased to {self.error_count}")
        
    def get_performance_summary(self) -> Dict:
        """Get a summary of performance metrics."""
        if not self.metrics_history:
            return {"error": "No metrics recorded"}
            
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        return {
            "total_frames": self.frame_count,
            "total_errors": self.error_count,
            "average_cpu": np.mean([m.cpu_percent for m in recent_metrics]),
            "average_memory": np.mean([m.memory_percent for m in recent_metrics]),
            "total_execution_time": recent_metrics[-1].execution_time if recent_metrics else 0,
            "fps": self.frame_count / recent_metrics[-1].execution_time if recent_metrics and recent_metrics[-1].execution_time > 0 else 0
        }
        
    def plot_performance(self, save_path: Optional[str] = None):
        """Plot performance metrics over time."""
        if not self.metrics_history:
            logger.warning("No metrics to plot")
            return
            
        timestamps = [m.timestamp for m in self.metrics_history]
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_percent for m in self.metrics_history]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # CPU usage plot
        ax1.plot(timestamps, cpu_values, 'b-', label='CPU %')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.set_title('System Performance Monitoring')
        ax1.grid(True)
        ax1.legend()
        
        # Memory usage plot
        ax2.plot(timestamps, memory_values, 'r-', label='Memory %')
        ax2.set_ylabel('Memory Usage (%)')
        ax2.set_xlabel('Time')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance plot saved to {save_path}")
        else:
            plt.show()

class DebugVisualizer:
    """Enhanced visualization tools for debugging."""
    
    @staticmethod
    def visualize_detection_results(image: np.ndarray, detections: List[Tuple], 
                                  depths: List[float], directions: List[float], 
                                  speeds: List[float], save_path: Optional[str] = None):
        """Visualize detection results with enhanced debugging information."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Original image with detections
        axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        for i, (x1, y1, x2, y2) in enumerate(detections):
            rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=2, edgecolor='red', facecolor='none')
            axes[0, 0].add_patch(rect)
            axes[0, 0].text(x1, y1-10, f'Person {i+1}', color='red', fontsize=10, fontweight='bold')
        axes[0, 0].set_title('Human Detection Results')
        axes[0, 0].axis('off')
        
        # Depth visualization
        if depths:
            axes[0, 1].bar(range(len(depths)), depths, color='blue', alpha=0.7)
            axes[0, 1].set_xlabel('Person ID')
            axes[0, 1].set_ylabel('Depth (cm)')
            axes[0, 1].set_title('Depth Estimation Results')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, depth in enumerate(depths):
                axes[0, 1].text(i, depth + 0.1, f'{depth:.1f}cm', ha='center', va='bottom')
        
        # Direction visualization
        if directions:
            angles = np.array(directions)
            x = np.cos(angles)
            y = np.sin(angles)
            axes[1, 0].scatter(x, y, c=range(len(directions)), cmap='viridis', s=100)
            axes[1, 0].set_xlim(-1.2, 1.2)
            axes[1, 0].set_ylim(-1.2, 1.2)
            axes[1, 0].set_xlabel('X Direction')
            axes[1, 0].set_ylabel('Y Direction')
            axes[1, 0].set_title('Direction Vectors')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].set_aspect('equal')
            
            # Add arrows to show directions
            for i, (angle, speed) in enumerate(zip(directions, speeds)):
                dx = np.cos(angle) * speed * 0.5
                dy = np.sin(angle) * speed * 0.5
                axes[1, 0].arrow(0, 0, dx, dy, head_width=0.1, head_length=0.1, 
                                fc='red', ec='red', alpha=0.7)
                axes[1, 0].text(dx*1.1, dy*1.1, f'P{i+1}', fontsize=8)
        
        # Speed visualization
        if speeds:
            axes[1, 1].bar(range(len(speeds)), speeds, color='green', alpha=0.7)
            axes[1, 1].set_xlabel('Person ID')
            axes[1, 1].set_ylabel('Speed (m/s)')
            axes[1, 1].set_title('Speed Estimation Results')
            axes[1, 1].grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, speed in enumerate(speeds):
                axes[1, 1].text(i, speed + 0.01, f'{speed:.2f}m/s', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Debug visualization saved to {save_path}")
        else:
            plt.show()
    
    @staticmethod
    def visualize_path_planning(cost_map: np.ndarray, path: List[Tuple], 
                             obstacles: np.ndarray, start: Tuple, goal: Tuple,
                             save_path: Optional[str] = None):
        """Visualize path planning results with debugging information."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Cost map visualization
        im1 = ax1.imshow(cost_map.T, cmap='hot', origin='lower')
        ax1.set_title('Cost Map')
        ax1.set_xlabel('X Position')
        ax1.set_ylabel('Y Position')
        plt.colorbar(im1, ax=ax1, label='Cost')
        
        # Path visualization
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            ax2.plot(path_x, path_y, 'r-', linewidth=2, label='Planned Path')
            ax2.scatter(path_x, path_y, c='red', s=50, zorder=5)
        
        # Start and goal markers
        ax2.scatter(start[0], start[1], c='green', s=200, marker='s', label='Start', zorder=5)
        ax2.scatter(goal[0], goal[1], c='blue', s=200, marker='*', label='Goal', zorder=5)
        
        # Obstacles
        if obstacles.size > 0:
            ax2.scatter(obstacles[:, 0], obstacles[:, 1], c='black', s=100, marker='x', label='Obstacles', zorder=5)
        
        ax2.set_title('Path Planning Results')
        ax2.set_xlabel('X Position')
        ax2.set_ylabel('Y Position')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Path planning visualization saved to {save_path}")
        else:
            plt.show()

class ErrorHandler:
    """Enhanced error handling and recovery."""
    
    def __init__(self):
        self.error_log: List[Dict] = []
        
    def handle_detection_error(self, error: Exception, context: str = ""):
        """Handle detection-related errors."""
        error_info = {
            "timestamp": datetime.now(),
            "type": "detection_error",
            "error": str(error),
            "context": context
        }
        self.error_log.append(error_info)
        logger.error(f"Detection error: {error} in context: {context}")
        
    def handle_pathfinding_error(self, error: Exception, context: str = ""):
        """Handle pathfinding-related errors."""
        error_info = {
            "timestamp": datetime.now(),
            "type": "pathfinding_error", 
            "error": str(error),
            "context": context
        }
        self.error_log.append(error_info)
        logger.error(f"Pathfinding error: {error} in context: {context}")
        
    def get_error_summary(self) -> Dict:
        """Get a summary of all errors."""
        if not self.error_log:
            return {"total_errors": 0}
            
        error_types = {}
        for error in self.error_log:
            error_type = error["type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return {
            "total_errors": len(self.error_log),
            "error_types": error_types,
            "recent_errors": self.error_log[-5:] if len(self.error_log) >= 5 else self.error_log
        }

# Global instances for easy access
performance_monitor = PerformanceMonitor()
error_handler = ErrorHandler()
