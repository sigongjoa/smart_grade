
import cv2
import numpy as np

def debug_contours(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Otsu's thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Try a larger kernel for closing to merge elements within a card
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} initial contours.")
    
    debug_img = image.copy()
    img_area = image.shape[0] * image.shape[1]
    
    isolated_count = 0
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        if area < img_area * 0.02: continue # Lowered threshold
        
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(debug_img, f"ID:{i} Area:{int(area)}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if isolated_count < 10:
            card_img = image[y:y+h, x:x+w]
            cv2.imwrite(f"debug_card_{isolated_count}.jpg", card_img)
            isolated_count += 1

    cv2.imwrite("debug_contours.jpg", debug_img)
    print(f"Saved debug_contours.jpg and isolated {isolated_count} cards.")

if __name__ == "__main__":
    debug_contours("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg")
