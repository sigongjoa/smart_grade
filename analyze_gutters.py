
import cv2
import numpy as np

def analyze_gutters(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    v_proj = np.sum(thresh, axis=1)
    v_proj_smoothed = np.convolve(v_proj, np.ones(50)/50, mode='same')
    
    h = img.shape[0]
    # Gutter 1 expected at ~1132
    gutter1_range = (int(h*0.3), int(h*0.4))
    min_v1 = np.argmin(v_proj_smoothed[gutter1_range[0]:gutter1_range[1]]) + gutter1_range[0]
    
    # Gutter 2 expected at ~2264
    gutter2_range = (int(h*0.6), int(h*0.7))
    min_v2 = np.argmin(v_proj_smoothed[gutter2_range[0]:gutter2_range[1]]) + gutter2_range[0]
    
    print(f"Deepest valley 1: {min_v1} (val: {v_proj_smoothed[min_v1]})")
    print(f"Deepest valley 2: {min_v2} (val: {v_proj_smoothed[min_v2]})")

if __name__ == "__main__":
    analyze_gutters("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
