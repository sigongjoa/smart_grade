
import cv2
import numpy as np
from engine.bubble_detector import BubbleDetector, BubbleDetectorConfig
from engine.document_processor import DocumentProcessor

def diagnose_card():
    image_path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    image = cv2.imread(image_path)
    if image is None: return
    
    # Take a middle card region for analysis
    h, w = image.shape[:2]
    card_crop = image[h//3:2*h//3, :]
    
    # Process card
    dp = DocumentProcessor()
    warped = dp.process_document_image(card_crop)
    if warped is None: warped = card_crop
    
    cv2.imwrite("diagnose_warped.jpg", warped)
    
    # Test different thresholds
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    
    for t in [150, 180, 200]:
        _, thresh = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite(f"diagnose_thresh_{t}.jpg", thresh)
        
        # Detect bubbles with this threshold
        detector = BubbleDetector(config=BubbleDetectorConfig(binary_threshold=t, min_bubble_size=10, max_bubble_size=120))
        bubbles = detector.detect_bubbles(warped)
        
        vis = warped.copy()
        for (bx, by, bw, bh, _) in bubbles:
            cv2.rectangle(vis, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
        cv2.imwrite(f"diagnose_bubbles_{t}.jpg", vis)
        print(f"Threshold {t}: Detected {len(bubbles)} bubbles.")

if __name__ == "__main__":
    diagnose_card()
