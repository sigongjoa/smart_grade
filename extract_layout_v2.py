
import cv2
import numpy as np

def extract_layout_info(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Adaptive thresholding to handle lighting variations
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 21, 10)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ar = w / float(h)
        # Relaxed constraints for smaller bubbles in 1000px width image
        if 5 <= w <= 25 and 5 <= h <= 25 and 0.6 <= ar <= 1.4:
            bubbles.append((x, y, w, h))
            
    # Sort bubbles by Y primarily, then X
    bubbles = sorted(bubbles, key=lambda b: (b[1] // 5, b[0]))
    
    print(f"Detected {len(bubbles)} bubbles.")
    
    # Save a visualization
    vis_img = image.copy()
    for (x, y, w, h) in bubbles:
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 0, 255), 1)
    cv2.imwrite("all_bubbles_detected_v2.jpg", vis_img)
    
    # Identify unique X positions (columns)
    if bubbles:
        xs = sorted([b[0] for b in bubbles])
        unique_xs = []
        if xs:
            curr_x = xs[0]
            count = 1
            for i in range(1, len(xs)):
                if abs(xs[i] - curr_x) < 5:
                    count += 1
                else:
                    if count >= 3: # Significant column
                        unique_xs.append((curr_x, count))
                    curr_x = xs[i]
                    count = 1
            if count >= 3:
                unique_xs.append((curr_x, count))
        
        print(f"Potential Columns (X, count): {unique_xs}")

if __name__ == "__main__":
    extract_layout_info("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
