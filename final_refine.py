
import cv2
import numpy as np

def final_refine(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV) # Sharper threshold
    
    # Very small kernel to preserve gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    img_h, img_w = image.shape[:2]
    img_area = img_h * img_w
    
    cards = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        
        # Lowered threshold to 0.05
        if area > img_area * 0.05:
            cards.append((x, y, w, h))
            
    cards = sorted(cards, key=lambda b: b[1])
    print(f"Isolated {len(cards)} cards.")
    
    for i, (x, y, w, h) in enumerate(cards):
        card_img = image[y:y+h, x:x+w]
        cv2.imwrite(f"final_card_{i}.jpg", card_img)
        print(f"Saved final_card_{i}.jpg: {w}x{h}")

if __name__ == "__main__":
    final_refine("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
