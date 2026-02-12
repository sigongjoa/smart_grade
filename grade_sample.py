
import cv2
import json
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from engine.yedam_grader import YeDamGrader

def main():
    image_path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    print(f"Loading sample image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image.")
        return

    print(f"Image resolution: {image.shape[1]}x{image.shape[0]}")
    
    grader = YeDamGrader()
    print("Processing page...")
    results = grader.process_page(image)
    
    print(f"Processed {len(results)} cards.")
    
    for i, res in enumerate(results):
        print(f"\n--- Card {i} ---")
        print(f"Registration: {res.get('registration', 'N/A')}")
        ans = res.get('answers', {})
        print(f"Answers Extracted: {len(ans)} questions found.")
        # Print first few answers
        sample_ans = {k: ans[k] for k in sorted(ans.keys())[:5]}
        print(f"Sample Answers (Q1-5): {sample_ans}")

    # Save detailed results to JSON
    output_json = "grading_results_sample.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        # Convert dictionary to be JSON serializable (handle list of indices)
        json.dump(results, f, indent=4)
    print(f"\nFull results saved to {output_json}")

if __name__ == "__main__":
    main()
