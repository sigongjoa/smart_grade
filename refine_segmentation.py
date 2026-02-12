
import cv2
import numpy as np

def refine_segmentation(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Use a smaller kernel to avoid merging separate cards
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort by area and take top ones
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    img_h, img_w = image.shape[:2]
    img_area = img_h * img_w
    
    cards = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        
        # Filter: Cards should be somewhat rectangular and have significant area
        if area > img_area * 0.1 and 0.5 < w/h < 2.0:
            cards.append((x, y, w, h))
            
    # Sort top-to-bottom
    cards = sorted(cards, key=lambda b: b[1])
    
    print(f"Isolated {len(cards)} cards after refinement.")
    
    for i, (x, y, w, h) in enumerate(cards):
        # Save each card
        card_img = image[y:y+h, x:x+w]
        cv2.imwrite(f"refined_card_{i}.jpg", card_img)
        print(f"Saved refined_card_{i}.jpg: {w}x{h}")
        
if __name__ == "__main__":
    refine_segmentation("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
