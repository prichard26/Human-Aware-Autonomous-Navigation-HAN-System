import os
import cv2

def resize_images_to_512(source_dir, target_dir):
    """
    Resizes all images in the source directory to 512x512 and saves them in the target directory with the same name.

    Args:
    - source_dir (str): Path to the source directory containing the images.
    - target_dir (str): Path to the target directory to save the resized images.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for filename in os.listdir(source_dir):
        if filename.endswith(".jpeg") or filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(source_dir, filename)
            img = cv2.imread(img_path)
            if img is None:
                print(f"Could not read image {img_path}. Skipping.")
                continue

            resized_img = cv2.resize(img, (2048, 2048))
            target_path = os.path.join(target_dir, filename)
            cv2.imwrite(target_path, resized_img)
            print(f"Resized and saved {filename} to {target_path}")

source_dir = "/Users/prichard/miniconda3/envs/infosys/cv_project/data/input/calibration/normal_size"
target_dir = "/Users/prichard/miniconda3/envs/infosys/cv_project/data/input/calibration/high_size"
resize_images_to_512(source_dir, target_dir)