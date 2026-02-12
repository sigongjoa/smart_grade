
import cv2
import numpy as np

def extract_layout_info(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ar = w / float(h)
        if 15 <= w <= 60 and 15 <= h <= 60 and 0.7 <= ar <= 1.3:
            bubbles.append((x, y, w, h))
            
    # Sort bubbles by Y primarily, then X
    bubbles = sorted(bubbles, key=lambda b: (b[1] // 10, b[0]))
    
    print(f"Detected {len(bubbles)} bubbles.")
    
    # Save a visualization of all detected bubbles
    vis_img = image.copy()
    for (x, y, w, h) in bubbles:
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
    cv2.imwrite("all_bubbles_detected.jpg", vis_img)
    
    # Analyze distribution
    xs = sorted([b[0] for b in bubbles])
    ys = sorted([b[1] for b in bubbles])
    
    print(f"X range: {xs[0]} to {xs[-1]}")
    print(f"Y range: {ys[0]} to {ys[-1]}")
    
    # Print bubble clusters (potential columns)
    if bubbles:
        curr_x = bubbles[0][0]
        count = 0
        for b in sorted(bubbles, key=lambda b: b[0]):
            if abs(b[0] - curr_x) < 30:
                count += 1
            else:
                if count > 5:
                    print(f"Column at X={curr_x} has {count} bubbles.")
                curr_x = b[0]
                count = 1
        print(f"Column at X={curr_x} has {count} bubbles.")

if __name__ == "__main__":
    extract_layout_info("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
