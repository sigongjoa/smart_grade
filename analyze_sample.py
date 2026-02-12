
import cv2
import numpy as np
import os

def analyze_omr(image_path):
    print(f"Analyzing {image_path}...")
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image.")
        return

    h, w = image.shape[:2]
    print(f"Dimensions: {w}x{h}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    bubbles = []
    for c in contours:
        (x, y, bw, bh) = cv2.boundingRect(c)
        ar = bw / float(bh)
        if 15 <= bw <= 50 and 15 <= bh <= 50 and 0.8 <= ar <= 1.2:
            bubbles.append((x, y, bw, bh))

    print(f"Detected {len(bubbles)} bubble candidates.")
    
    # Sort bubbles by X to find groups
    bubbles = sorted(bubbles, key=lambda b: b[0])
    
    # Find columns
    cols = []
    if bubbles:
        curr_col = [bubbles[0]]
        for i in range(1, len(bubbles)):
            if abs(bubbles[i][0] - curr_col[-1][0]) < 20:
                curr_col.append(bubbles[i])
            else:
                cols.append(curr_col)
                curr_col = [bubbles[i]]
        cols.append(curr_col)

    print(f"Found {len(cols)} potential columns.")
    for i, col in enumerate(cols):
        col_sorted = sorted(col, key=lambda b: b[1])
        print(f"Column {i}: {len(col)} bubbles, X range: {col_sorted[0][0]}-{col_sorted[-1][0]}, Y range: {col_sorted[0][1]}-{col_sorted[-1][1]}")

if __name__ == "__main__":
    analyze_omr("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
