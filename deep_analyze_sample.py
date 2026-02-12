
import cv2
import numpy as np
from engine.ocr_engine import OCREngine

def deep_analyze(image_path):
    image = cv2.imread(image_path)
    if image is None: return
    
    ocr = OCREngine(lang='ko')
    elements = ocr.identify_structural_elements(image)
    print(f"Structural Elements: {elements}")
    
    text_results = ocr.extract_text(image)
    for res in text_results:
        if res['confidence'] > 0.5:
            print(f"Text: {res['text']} at {res['bbox']}")

if __name__ == "__main__":
    deep_analyze("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
