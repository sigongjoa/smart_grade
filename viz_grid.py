
import cv2
import numpy as np

def visualize_extrapolation(image_path, y_start, y_end):
    img = cv2.imread(image_path)
    if img is None: return
    
    card_crop = img[y_start:y_end, :]
    gray = cv2.cvtColor(card_crop, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 21, 15)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if 10 <= w <= 100 and 10 <= h <= 100 and 0.7 <= w/h <= 1.3:
            bubbles.append((x + w/2, y + h/2))
            
    # Simulate finding Reg Params
    xs = sorted([b[0] for b in bubbles if b[0] < img.shape[1] * 0.25])
    # Assume we find peaks (simplifying for visual)
    col_peaks = [xs[0], xs[int(len(xs)*0.25)], xs[int(len(xs)*0.5)], xs[int(len(xs)*0.75)], xs[-1]]
    x0, dx = col_peaks[0], (col_peaks[-1] - col_peaks[0]) / 4
    
    ys = sorted([b[1] for b in bubbles if b[0] < img.shape[1] * 0.25])
    y0, dy = ys[0], (ys[-1] - ys[0]) / 9
    
    # Draw Grid
    viz = card_crop.copy()
    for bx, by in bubbles:
        cv2.circle(viz, (int(bx), int(by)), 5, (0, 255, 0), -1)
        
    block_offsets = [7.5, 11.0, 14.5, 18.0]
    for b_off in block_offsets:
        for c in range(5):
            gx = int(x0 + (b_off + c*0.5) * dx)
            cv2.line(viz, (gx, 0), (gx, img.shape[0]), (0, 0, 255), 1)
            
    for r in range(10):
        gy = int(y0 + r * dy)
        cv2.line(viz, (0, gy), (img.shape[1], gy), (255, 0, 0), 1)
        
    cv2.imwrite("viz_extrapolated_grid.jpg", viz)
    print("Viz saved: viz_extrapolated_grid.jpg")

if __name__ == "__main__":
    visualize_extrapolation("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", 0, 1111)
