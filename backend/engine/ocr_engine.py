try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

import cv2
import numpy as np

class OCREngine:
    def __init__(self, use_gpu=False, lang='en'):
        """
        Initialize PaddleOCR with lightweight models.
        'ko' for Korean support, 'en' for English.
        """
        if PaddleOCR:
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        else:
            self.ocr = None
            print("Warning: PaddleOCR not installed. OCR functionality will be limited.")

    def extract_text(self, image):
        """Extract all text from an image."""
        if not self.ocr:
            return []
            
        try:
            result = self.ocr.ocr(image)
        except Exception as e:
            print(f"OCR Error: {e}")
            return []

        if not result or not result[0]:
            return []
            
        parsed_results = []
        
        # Handle new dictionary-style structure (e.g. from newer PaddleX versions)
        if isinstance(result[0], dict):
            res_dict = result[0]
            texts = res_dict.get('rec_texts', [])
            scores = res_dict.get('rec_scores', [])
            # Prefer rec_boxes, fallback to rec_polys
            boxes = res_dict.get('rec_boxes', res_dict.get('rec_polys', []))
            
            for i in range(len(texts)):
                try:
                    box = boxes[i]
                    if hasattr(box, 'tolist'):
                        box = box.tolist()
                    
                    parsed_results.append({
                        "text": str(texts[i]),
                        "confidence": float(scores[i]) if i < len(scores) else 0.0,
                        "bbox": box if i < len(boxes) else None
                    })
                except Exception:
                    continue
        else:
            # Handle classic list-of-lists structure
            for line in result[0]:
                try:
                    # line is typically [ [bbox], (text, confidence) ]
                    if len(line) >= 2 and isinstance(line[1], (list, tuple)):
                        text = line[1][0]
                        conf = float(line[1][1])
                    else:
                        # Fallback if structure is different
                        text = str(line[1]) if len(line) > 1 else ""
                        conf = 0.0
                    
                    bbox = line[0]
                    if hasattr(bbox, 'tolist'):
                        bbox = bbox.tolist()
                        
                    parsed_results.append({
                        "text": str(text),
                        "confidence": float(conf),
                        "bbox": bbox
                    })
                except (IndexError, TypeError, ValueError) as e:
                    print(f"Skipping malformed OCR line: {line}. Error: {e}")
                    continue
            
        return parsed_results

    def extract_from_region(self, image, bbox):
        """
        Extract text from a specific region (x, y, w, h).
        """
        x, y, w, h = bbox
        roi = image[y:y+h, x:x+w]
        return self.extract_text(roi)

    def identify_structural_elements(self, image):
        """
        Identify anchors like 'Name', 'Student ID', or 'Score' to help alignment.
        """
        full_text = self.extract_text(image)
        elements = {}
        
        keywords = {
            "이름": "name_box",
            "학번": "id_box",
            "점수": "score_box"
        }
        
        for item in full_text:
            for kw, key in keywords.items():
                if kw in item["text"]:
                    elements[key] = item["bbox"]
                    
        return elements

if __name__ == "__main__":
    # engine = OCREngine()
    # results = engine.extract_text(cv2.imread("warped.jpg"))
    pass
