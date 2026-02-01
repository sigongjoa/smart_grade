import cv2
import numpy as np

class BubbleDetector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def detect_bubbles(self, warped_image):
        gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological opening to remove thin grid lines
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # RETR_LIST detects bubbles inside boxes
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        bubble_candidates = []
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            
            # Extremely permissive filters for bubbles (any small blob around 10-50px)
            if 8 <= w <= 100 and 8 <= h <= 100 and 0.4 <= ar <= 2.5:
                # Basic area filter to remove tiny specs
                if cv2.contourArea(c) > 20:
                    bubble_candidates.append((x, y, w, h, c))
        
        bubble_candidates = sorted(bubble_candidates, key=lambda b: b[0])
        deduped = []
        for i in range(len(bubble_candidates)):
            is_duplicate = False
            for j in range(len(deduped)):
                # If centers are very close, it's a duplicate (inner/outer contour)
                dist = np.sqrt((bubble_candidates[i][0] - deduped[j][0])**2 + 
                              (bubble_candidates[i][1] - deduped[j][1])**2)
                if dist < 5:
                    is_duplicate = True
                    break
            if not is_duplicate:
                deduped.append(bubble_candidates[i])
        
        return deduped

    def detect_columns(self, bubbles, col_threshold=50):
        if not bubbles: return []
        # Sort by X
        bubbles = sorted(bubbles, key=lambda b: b[0])
        columns = []
        current_col = [bubbles[0]]
        for i in range(1, len(bubbles)):
            if abs(bubbles[i][0] - current_col[-1][0]) < col_threshold:
                current_col.append(bubbles[i])
            else:
                columns.append(sorted(current_col, key=lambda b: b[1]))
                current_col = [bubbles[i]]
        columns.append(sorted(current_col, key=lambda b: b[1]))
        return columns

    def sort_into_grid(self, bubbles, row_threshold=15):
        """
        Groups bubbles into rows. For multi-column, this should be called per column.
        """
        if not bubbles: return []
        # Sort by Y
        bubbles = sorted(bubbles, key=lambda b: b[1])
        rows = []
        current_row = [bubbles[0]]
        for i in range(1, len(bubbles)):
            if abs(bubbles[i][1] - current_row[0][1]) < row_threshold:
                current_row.append(bubbles[i])
            else:
                rows.append(sorted(current_row, key=lambda b: b[0]))
                current_row = [bubbles[i]]
        rows.append(sorted(current_row, key=lambda b: b[0]))
        return rows

    def check_marking(self, warped_image, bubbles):
        gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        results = []
        for (x, y, w, h, c) in bubbles:
            roi = gray[y:y+h, x:x+w]
            avg_intensity = np.mean(roi)
            marking_score = (255 - avg_intensity) / 255.0
            
            # Slightly lower threshold for robustness
            is_marked = marking_score > 0.35 
            
            results.append({"bbox": (x, y, w, h), "score": float(marking_score), "is_marked": bool(is_marked)})
        return results

    def grade_paper(self, warped_image, answer_key_mapping):
        bubbles = self.detect_bubbles(warped_image)
        grid = self.sort_into_grid(bubbles)
        graded_results = {}
        for i, row in enumerate(grid):
            marking_status = self.check_marking(warped_image, row)
            marked_indices = [idx for idx, res in enumerate(marking_status) if res["is_marked"]]
            graded_results[i + 1] = {"selected": marked_indices, "confidence": [res["score"] for res in marking_status]}
        return graded_results
