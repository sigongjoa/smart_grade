import cv2
import os
from engine.omr_grid_detector import OMRGridDetector, GridDetectorConfig

def test_grid_detection(image_path, output_dir):
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to read image")
        return
    
    detector = OMRGridDetector()
    cards = detector.detect_cards(image)
    print(f"Detected {len(cards)} cards")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save a visualization of detected regions
    vis_image = image.copy()
    bboxes = detector._detect_card_regions(image)
    for i, (x, y, w, h) in enumerate(bboxes):
        cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 5)
        cv2.putText(vis_image, f"Card {i}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
    
    # Resize for visualization
    scale = 0.2
    vis_small = cv2.resize(vis_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(output_dir, "grid_detection_vis.jpg"), vis_small)
    
    # Save individual cards
    for i, card in enumerate(cards):
        cv2.imwrite(os.path.join(output_dir, f"card_{i}.jpg"), card)
        print(f"Saved card {i} to {output_dir}")

if __name__ == "__main__":
    sample_path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    output_dir = "/mnt/d/progress/mathesis/node13_smart_grader/test_results/grid_test"
    test_grid_detection(sample_path, output_dir)
