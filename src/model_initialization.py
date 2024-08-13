import torch
import tensorflow_hub as hub
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

def load_yolo_model():
    """
    Loads the YOLO model from Ultralytics.
    """
    return torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

def load_posenet_model():
    """
    Loads the MoveNet model from TensorFlow Hub.
    """
    posenet_model = hub.load('https://tfhub.dev/google/movenet/singlepose/lightning/3')
    return posenet_model.signatures['serving_default']

def load_depth_estimation_model():
    """
    Loads the depth estimation model.
    """
    processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-small-hf")
    model = AutoModelForDepthEstimation.from_pretrained("LiheYoung/depth-anything-small-hf")
    return processor, model
