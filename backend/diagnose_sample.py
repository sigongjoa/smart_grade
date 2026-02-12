import cv2
import numpy as np
import os
import sys
from engine.bubble_detector import BubbleDetector, BubbleDetectorConfig

def diagnose_sample(image_path, output_path):
    print(f"Analyzing {image_path}...")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return

    print(f"Image shape: {image.shape}")
    
    # Detect bubbles with default config
    detector = BubbleDetector()
    bubbles = detector.detect_bubbles(image)
    print(f"Total bubbles detected with defaults: {len(bubbles)}")
    
    # Draw bubbles on image for visualization
    vis_image = image.copy()
    for (x, y, w, h, c) in bubbles:
        cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Save a smaller version for inspection
    scale_percent = 20 # percent of original size
    width = int(vis_image.shape[1] * scale_percent / 100)
    height = int(vis_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    resized = cv2.resize(vis_image, dim, interpolation = cv2.INTER_AREA)
    cv2.imwrite(output_path, resized)
    print(f"Saved visualization to {output_path}")

    # Check some marking scores
    if bubbles:
        # Check first 10 bubbles
        marking_results = detector.check_marking(image, bubbles[:10])
        for i, res in enumerate(marking_results):
            print(f"Bubble {i}: Score {res['score']:.4f}, Marked: {res['is_marked']}")

if __name__ == "__main__":
    sample_path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    output_path = "/mnt/d/progress/mathesis/node13_smart_grader/test_results/diagnosis_vis.jpg"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    diagnose_sample(sample_path, output_path)
