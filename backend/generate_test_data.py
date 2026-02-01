import cv2
import numpy as np
import json
import os

def generate_synthetic_omr(output_path, truth_path, num_questions=10):
    # Create white canvas (A4 ratio approx)
    width, height = 800, 1000
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw simple header
    cv2.putText(img, "Smart-Grader Synthetic Test", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    truth = {}
    
    start_y = 150
    spacing_y = 60
    bubble_radius = 15
    bubble_spacing_x = 60
    
    for q in range(1, num_questions + 1):
        y = start_y + (q-1) * spacing_y
        cv2.putText(img, f"Q{q:02d}", (50, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Select one random bubble as the "student's answer"
        correct_choice = (q % 5) + 1 # Deterministic for test
        truth[str(q)] = correct_choice
        
        for choice in range(1, 6):
            x = 150 + (choice-1) * bubble_spacing_x
            
            # Draw the bubble (circle)
            if choice == correct_choice:
                # Filled bubble for the correct choice
                cv2.circle(img, (x, y), bubble_radius, (0, 0, 0), -1)
            else:
                # Empty bubble for others
                cv2.circle(img, (x, y), bubble_radius, (0, 0, 0), 2)
                
            # Put numbers inside or near (optional)
            cv2.putText(img, str(choice), (x - 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

    # Add a bit of noise/blur to simulate a "clean scan"
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    cv2.imwrite(output_path, img)
    with open(truth_path, 'w') as f:
        json.dump(truth, f, indent=4)
    
    print(f"Generated synthetic OMR: {output_path}")
    print(f"Generated truth JSON: {truth_path}")

if __name__ == "__main__":
    os.makedirs("test_data", exist_ok=True)
    generate_synthetic_omr("test_data/synthetic_omr.jpg", "test_data/truth.json")
