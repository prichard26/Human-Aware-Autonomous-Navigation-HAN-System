import torch
import tensorflow_hub as hub
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

def load_yolo_model():
    """
    Loads the YOLOv5 model directly from the Ultralytics hub.
    """
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
    print("YOLOv5 model loaded successfully.")
    return model

def load_posenet_model():
    """
    Loads the MoveNet model directly from TensorFlow Hub.
    """
    model = hub.load('https://tfhub.dev/google/movenet/singlepose/lightning/3').signatures['serving_default']
    print("MoveNet (PoseNet) model loaded successfully.")
    return model

def load_depth_estimation_model():
    """
    Loads the depth estimation model directly from Hugging Face hub.
    """
    processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-small-hf")
    model = AutoModelForDepthEstimation.from_pretrained("LiheYoung/depth-anything-small-hf")
    print("Depth estimation model loaded successfully.")
    return processor, model