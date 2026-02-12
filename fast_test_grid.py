
import cv2
import numpy as np

def fast_grid_detection(image_path):
    image = cv2.imread(image_path)
    if image is None: 
        print("Failed to load image")
        return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Binary thresholding for the cards (which are typically lighter than background or have clear borders)
    # The sample has 3 cards with clear white backgrounds.
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Morphological closing to merge the card contents into a single block
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} initial contours.")
    
    cards = []
    img_area = image.shape[0] * image.shape[1]
    
    # Sort by Y position
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        if area < img_area * 0.05: continue # Too small
        
        x, y, w, h = cv2.boundingRect(c)
        print(f"Card {i} candidate: Area {area}, BBox ({x}, {y}, {w}, {h})")
        
        # Crop and save
        card_img = image[y:y+h, x:x+w]
        cv2.imwrite(f"fast_card_{i}.jpg", card_img)
        cards.append(card_img)

    print(f"Isolated {len(cards)} cards.")

if __name__ == "__main__":
    fast_grid_detection("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
