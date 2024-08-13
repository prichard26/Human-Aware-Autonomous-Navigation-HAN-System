"""
depth_estimation.py
Contains functions for depth estimation using pre-trained models.
"""

from PIL import Image
import torch
import numpy as np
import cv2

def estimate_depth(image, processor, model):
    """
    Estimates the depth of the image using a pre-trained model.
    
    Args:
    - image (PIL Image or numpy array): The input image.
    - processor (AutoImageProcessor): The image processor.
    - model (AutoModelForDepthEstimation): The depth estimation model.
    
    Returns:
    - depth_image (PIL Image): Depth image.
    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        predicted_depth = outputs.predicted_depth
    prediction = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image.size[::-1],
        mode="bicubic",
        align_corners=False,
    )
    output = prediction.squeeze().cpu().numpy()
    formatted = (output * 255 / np.max(output)).astype("uint8")
    depth_image = Image.fromarray(formatted)
    return depth_image
