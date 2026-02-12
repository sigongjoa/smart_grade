
import cv2
import numpy as np

def debug_v_proj(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    # 1. Basic Inversion
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    v_proj = np.sum(thresh, axis=1)
    
    print(f"Image height: {img.shape[0]}")
    print(f"V_proj min: {np.min(v_proj)}")
    print(f"V_proj max: {np.max(v_proj)}")
    print(f"V_proj mean: {np.mean(v_proj)}")
    print(f"V_proj 10th pct: {np.percentile(v_proj, 10)}")
    print(f"V_proj 90th pct: {np.percentile(v_proj, 90)}")

    # 2. Otsu Inversion
    _, thresh_otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    v_proj_otsu = np.sum(thresh_otsu, axis=1)
    
    print(f"--- OTSU ---")
    print(f"V_proj min: {np.min(v_proj_otsu)}")
    print(f"V_proj max: {np.max(v_proj_otsu)}")
    print(f"V_proj mean: {np.mean(v_proj_otsu)}")
    print(f"V_proj 10th pct: {np.percentile(v_proj_otsu, 10)}")

if __name__ == "__main__":
    debug_v_proj("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
