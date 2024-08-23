import torch
import joblib
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

def load_orientation_model():
    # CHANGE the path depending on which angles of orientation you would like to train
    orientation_model = joblib.load("/Users/paulrichard/Documents/HAAN/model/orientation_model.pkl")
    return orientation_model

def load_depth_curve_spec():
    best_model = "Polynomial"
    prediction_param = (0.00029224, -0.10041, 8.3828)
    return best_model, prediction_param