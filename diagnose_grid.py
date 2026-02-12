
import cv2
import numpy as np

def diagnose_card(image_path, y_start, y_end, idx):
    img = cv2.imread(image_path)
    if img is None: return
    
    card_crop = img[y_start:y_end, :]
    gray = cv2.cvtColor(card_crop, cv2.COLOR_BGR2GRAY)
    
    # Simulate adaptive detection
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 21, 10)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    diagnose_img = card_crop.copy()
    
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        if 10 <= w <= 100 and 10 <= h <= 100 and 0.7 <= ar <= 1.3:
            cv2.rectangle(diagnose_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
    # Draw expected grid lines
    h, w = card_crop.shape[:2]
    # Registration columns
    for c in range(5):
        cx = int(w * (0.05 + c * 0.05))
        cv2.line(diagnose_img, (cx, 0), (cx, h), (255, 0, 0), 1)
    
    # Question columns
    col_group_start = [0.38, 0.53, 0.68, 0.83]
    for start_pct in col_group_start:
        gx = int(w * start_pct)
        cv2.line(diagnose_img, (gx, 0), (gx, h), (0, 0, 255), 1)
        
    cv2.imwrite(f"diagnose_card_{idx}.jpg", diagnose_img)
    print(f"Diagnose image saved: diagnose_card_{idx}.jpg")

if __name__ == "__main__":
    split_points = [0, 1111, 2121, 3396]
    for i in range(3):
        diagnose_card("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", split_points[i], split_points[i+1], i)
