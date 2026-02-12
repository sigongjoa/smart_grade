
import cv2
from engine.omr_grid_detector import OMRGridDetector

def test_grid_detection(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    detector = OMRGridDetector()
    cards = detector.detect_cards(image)
    print(f"Detected {len(cards)} cards.")
    
    for i, card in enumerate(cards):
        cv2.imwrite(f"card_{i}.jpg", card)
        print(f"Saved card_{i}.jpg (size: {card.shape})")

if __name__ == "__main__":
    test_grid_detection("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
