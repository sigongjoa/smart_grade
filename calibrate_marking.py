
import cv2
import numpy as np

def calibrate_marking(image_path, y_start, y_end):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    card_crop = img[y_start+10:y_end-10, :]
    thresh = cv2.adaptiveThreshold(card_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 21, 15)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    intensities = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if 10 <= w <= 100 and 10 <= h <= 100 and 0.7 <= w/h <= 1.3:
            roi = card_crop[y:y+h, x:x+w]
            if roi.size > 0:
                intensities.append(np.mean(roi))
    
    intensities = sorted(intensities)
    print(f"Bubble intensity range: {min(intensities)} to {max(intensities)}")
    print(f"10th pct: {np.percentile(intensities, 10)}")
    print(f"25th pct: {np.percentile(intensities, 25)}")
    print(f"50th pct: {np.percentile(intensities, 50)}")
    print(f"75th pct: {np.percentile(intensities, 75)}")
    print(f"90th pct: {np.percentile(intensities, 90)}")

if __name__ == "__main__":
    split_points = [0, 1111, 2121, 3396]
    calibrate_marking("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", split_points[0], split_points[1])
