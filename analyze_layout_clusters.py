
import cv2
import numpy as np

def analyze_y_distribution(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 21, 10)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ar = w / float(h)
        if 5 <= w <= 25 and 5 <= h <= 25 and 0.6 <= ar <= 1.4:
            bubbles.append((x, y, w, h))
            
    # Group by Y ranges (cards)
    ys = sorted([b[1] for b in bubbles])
    card_ranges = []
    if ys:
        start_y = ys[0]
        for i in range(1, len(ys)):
            if ys[i] - ys[i-1] > 100: # Gap between cards
                card_ranges.append((start_y, ys[i-1]))
                start_y = ys[i]
        card_ranges.append((start_y, ys[-1]))
        
    print(f"Card Y ranges: {card_ranges}")
    
    # Process first card to find column structure
    if card_ranges:
        cy1, cy2 = card_ranges[0]
        card_bubbles = [b for b in bubbles if cy1 <= b[1] <= cy2]
        print(f"Card 0 has {len(card_bubbles)} bubbles.")
        
        # registration section (left)
        reg_bubbles = [b for b in card_bubbles if b[0] < 200]
        # question section (right)
        q_bubbles = [b for b in card_bubbles if b[0] >= 200]
        
        # Group reg_bubbles by X
        reg_xs = sorted(list(set([b[0] // 5 * 5 for b in reg_bubbles])))
        print(f"Registration X clusters: {reg_xs}")
        
        # Group q_bubbles by X
        q_xs = sorted(list(set([b[0] // 5 * 5 for b in q_bubbles])))
        print(f"Question X clusters: {q_xs}")

if __name__ == "__main__":
    analyze_y_distribution("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
