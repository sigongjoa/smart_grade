import cv2
import os
import json
from engine.bubble_detector import BubbleDetector
from engine.omr_grid_detector import OMRGridDetector

def verify_extracted_cards(grid_test_dir):
    detector = BubbleDetector()
    grid_detector = OMRGridDetector()
    
    # We found 3 cards
    for i in range(3):
        card_path = os.path.join(grid_test_dir, f"card_{i}.jpg")
        print(f"\nVerifying {card_path}...")
        
        card_img = cv2.imread(card_path)
        if card_img is None:
            print(f"Failed to load {card_path}")
            continue
            
        # Detect bubbles on isolated card
        bubbles = detector.detect_bubbles(card_img)
        print(f"Total bubbles: {len(bubbles)}")
        
        # Detect columns
        columns = detector.detect_columns(bubbles)
        print(f"Total columns: {len(columns)}")
        
        # Visualize for manual check
        marking_results = detector.check_marking(card_img, bubbles)
        vis_image = card_img.copy()
        for res in marking_results:
            x, y, w, h = res["bbox"]
            color = (0, 255, 0) if res["is_marked"] else (0, 0, 255)
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
        
        cv2.imwrite(os.path.join(grid_test_dir, f"card_{i}_bubbles.jpg"), vis_image)
        
        # Try full card processing
        try:
            # Note: _process_single_card is internal, but we can use it for testing
            # col_threshold=60, question_x_offset=300, num_question_cols=4, questions_per_col=10
            # From the image, the offset might be smaller for these forms
            # Let's try to see where bubbles are
            if bubbles:
                min_x = min(b[0] for b in bubbles)
                max_x = max(b[0] for b in bubbles)
                print(f"Bubble X range: {min_x} to {max_x}")
            
            result = grid_detector._process_single_card(
                card_img, i, 
                col_threshold=60, 
                question_x_offset=200, # Adjusted for these smaller forms
                num_question_columns=4, 
                questions_per_column=10
            )
            print(f"Student Name: {result.student_name}")
            print(f"Total questions graded: {len(result.answers)}")
            
            # Print first few answers
            for q in sorted(result.answers.keys())[:5]:
                print(f"Q{q}: {result.answers[q]}")
                
        except Exception as e:
            print(f"Error processing card: {e}")

if __name__ == "__main__":
    grid_test_dir = "/mnt/d/progress/mathesis/node13_smart_grader/test_results/grid_test"
    verify_extracted_cards(grid_test_dir)
