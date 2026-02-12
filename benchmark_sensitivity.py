
import cv2
import numpy as np

def benchmark_sensitivity(image_path, y_start, y_end):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    card_crop = img[y_start+10:y_end-10, :]
    results = []
    
    for c_val in [5, 10, 15, 20, 25]:
        thresh = cv2.adaptiveThreshold(card_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 21, c_val)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if 10 <= w <= 100 and 10 <= h <= 100 and 0.7 <= ar <= 1.3:
                count += 1
        results.append((c_val, count))
    
    print(f"Benchmark Results (C_val, Bubble Count): {results}")

if __name__ == "__main__":
    split_points = [0, 1111, 2121, 3396]
    benchmark_sensitivity("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", split_points[0], split_points[1])
