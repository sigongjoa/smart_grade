import cv2
import numpy as np
import json
import os
import random

def generate_ss03_omr(output_path, truth_path):
    # Dimensions: 20cm x 8cm -> 1300x480px (enough padding)
    w, h = 1300, 480
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    # 1. Background Grid & Boxes (Teal/Cyan color)
    line_color = (180, 180, 100) # Cyan-ish
    # Outer Border
    cv2.rectangle(img, (20, 20), (w-20, h-20), line_color, 2)
    
    # Section Dividers
    # Left Section (Personal Info): ~30% of width
    personal_info_w = 400
    cv2.line(img, (personal_info_w, 20), (personal_info_w, h-20), line_color, 2)
    
    # Right Sections (Questions): 4 columns
    col_w = (w - personal_info_w - 40) // 4
    for i in range(1, 4):
        x = personal_info_w + i * col_w
        cv2.line(img, (x, 20), (x, h-20), line_color, 1)

    # 2. Draw Question Layout (1-40)
    bubble_color = (100, 100, 255) # Red-ish (BGR)
    truth = {"answers": {}, "student_id": "10405"}
    
    # Question columns setup
    for col in range(4):
        start_q = col * 10 + 1
        base_x = personal_info_w + col * col_w + 30
        
        for q_offset in range(10):
            q_num = start_q + q_offset
            y = 100 + q_offset * 35
            
            # Question Number
            cv2.putText(img, f"{q_num:02d}", (base_x - 15, y + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            
            # Select random answer for truth
            correct_choice = random.randint(1, 5)
            truth["answers"][str(q_num)] = correct_choice
            
            # Draw 5 bubbles
            for choice in range(1, 6):
                bx = base_x + choice * 35
                
                if choice == correct_choice:
                    # MARKED WITH BLACK PEN (Simulation)
                    cv2.circle(img, (bx, y), 11, (10, 10, 10), -1)
                else:
                    # EMPTY RED BUBBLE - thickness 2
                    cv2.circle(img, (bx, y), 11, bubble_color, 2)
                    cv2.putText(img, str(choice), (bx - 5, y + 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, bubble_color, 1)

    # 3. Draw Personal Info Section (Left)
    # Class, Grade, Student ID grid simulation
    cv2.putText(img, "Class/ID Info", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    for row in range(10):
        for col in range(5):
            x = 80 + col * 35
            y = 120 + row * 25
            
            # Simulating ID: "10405"
            digit = str(row)
            is_student_id_mark = False
            if col == 0 and row == 1: is_student_id_mark = True
            if col == 1 and row == 0: is_student_id_mark = True
            if col == 2 and row == 4: is_student_id_mark = True
            if col == 3 and row == 0: is_student_id_mark = True
            if col == 4 and row == 5: is_student_id_mark = True
            
            if is_student_id_mark:
                cv2.circle(img, (x, y), 10, (10, 10, 10), -1)
            else:
                # Increased thickness to 2 for better detection
                cv2.circle(img, (x, y), 10, bubble_color, 2)

    # Add a border around the personal info section to help sorting logic
    cv2.rectangle(img, (40, 90), (350, 420), line_color, 1)
    # Add some 'Logo' or 'SS-03' text for anchor testing
    cv2.putText(img, "SS-03", (w - 70, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Save files
    cv2.imwrite(output_path, img)
    with open(truth_path, 'w', encoding='utf-8') as f:
        json.dump(truth, f, indent=4, ensure_ascii=False)
    
    print(f"Generated SS-03 OMR (No Timing Marks): {output_path}")

if __name__ == "__main__":
    os.makedirs("test_data", exist_ok=True)
    generate_ss03_omr("test_data/ss03_omr_marked.jpg", "test_data/ss03_truth.json")
