import cv2
import os

def create_thumbnail(image_path, output_path):
    print(f"Reading {image_path}...")
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to read image")
        return
    
    print(f"Size: {image.shape}")
    scale = 0.2
    small = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imwrite(output_path, small)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    create_thumbnail("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", "/mnt/d/progress/mathesis/node13_smart_grader/test_results/thumbnail.jpg")
