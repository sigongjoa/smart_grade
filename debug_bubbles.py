
import cv2
import numpy as np

def debug_bubbles(image_path, y_start, y_end, idx):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    
    card_crop = img[y_start+10:y_end-10, :]
    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(card_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 21, 10)
    
    cv2.imwrite(f"debug_thresh_card_{idx}.jpg", thresh)
    print(f"Debug threshold image saved: debug_thresh_card_{idx}.jpg")
    
    # Let's also save the raw gray crop
    cv2.imwrite(f"debug_gray_card_{idx}.jpg", card_crop)

if __name__ == "__main__":
    split_points = [0, 1111, 2121, 3396]
    for i in range(3):
        debug_bubbles("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", split_points[i], split_points[i+1], i)
