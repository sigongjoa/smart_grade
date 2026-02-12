
import cv2
import numpy as np
from typing import Dict, List, Any, Optional
from .document_processor import DocumentProcessor
from .bubble_detector import BubbleDetector, BubbleDetectorConfig

class YeDamGrader:
    """Specialized grader for Ye-dam OMR layout (3 cards per page)."""

    def __init__(self, bubble_detector: Optional[BubbleDetector] = None, doc_processor: Optional[DocumentProcessor] = None):
        self.bubble_detector = bubble_detector or BubbleDetector(
            config=BubbleDetectorConfig(
                min_bubble_size=10,
                max_bubble_size=120,
                marking_threshold=0.30, # Slightly more sensitive
                binary_threshold=180
            )
        )
        self.doc_processor = doc_processor or DocumentProcessor()

    def process_page(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Process a full page containing 3 cards using projection-based segmentation."""
        # 1. Convert to grayscale and invert
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 2. Vertical Projection to find card gutters
        # Use Otsu to get a better binary image for projection
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        v_proj = np.sum(thresh, axis=1)
        v_proj_smoothed = np.convolve(v_proj, np.ones(50)/50, mode='same')
        h_total = image.shape[0]
        
        # We KNOW there are 3 cards, so we find the two best split points in the expected gutter ranges
        gutter1_min = np.argmin(v_proj_smoothed[int(h_total*0.3):int(h_total*0.45)]) + int(h_total*0.3)
        gutter2_min = np.argmin(v_proj_smoothed[int(h_total*0.6):int(h_total*0.75)]) + int(h_total*0.6)
        
        split_points = [0, gutter1_min, gutter2_min, h_total]
        print(f"Adaptive split points: {split_points}")

        results = []
        for i in range(3):
            y_start, y_end = split_points[i], split_points[i+1]
            # Crop with small inner padding to avoid edge noise
            card_crop = image[y_start+10:y_end-10, :]
            
            # Align card
            warped = self.doc_processor.process_document_image(card_crop)
            if warped is None: warped = card_crop
            
            # Detect with adaptive thresholding
            final_bubbles = self._detect_bubbles_adaptive(warped)
            
            # Process card using detected bubbles
            card_res = self._process_card_v2(warped, final_bubbles)
            card_res["card_index"] = i
            results.append(card_res)
            
        return results

    def _process_card_v2(self, image: np.ndarray, bubbles: List[Any]) -> Dict[str, Any]:
        """Auto-calculate grid from bubbles."""
        h, w = image.shape[:2]
        if not bubbles:
            return {"registration": "", "answers": {}}

        # Map bubbles to their centers
        centers = [(x + w_b/2, y + h_b/2) for (x, y, w_b, h_b) in bubbles]
        
        # 1. Registration (Left ~25% of card)
        reg_centers = [c for c in centers if c[0] < w * 0.25]
        reg_id = self._extract_registration_auto(reg_centers, h, w)
        
        # 2. Questions (Right 75%)
        q_centers = [c for c in centers if c[0] >= w * 0.25]
        answers = self._extract_questions_auto(q_centers, h, w)
        
        return {
            "registration": reg_id,
            "answers": answers
        }

    def _extract_registration_auto(self, centers: List[tuple], h: int, w: int) -> str:
        if not centers: return ""
        # Find 5 dominant X columns
        xs = [c[0] for c in centers]
        if not xs: return ""
        
        # Cluster X into 5 columns
        xs = sorted(xs)
        col_peaks = []
        if xs:
            curr_col = [xs[0]]
            for i in range(1, len(xs)):
                if xs[i] - xs[i-1] > 20: 
                    col_peaks.append(np.mean(curr_col))
                    curr_col = [xs[i]]
                else:
                    curr_col.append(xs[i])
            col_peaks.append(np.mean(curr_col))
        
        # We expect 5 columns
        if len(col_peaks) < 1: return ""
        
        # Find 10 dominant Y rows for registration
        ys = [c[1] for c in centers]
        ys = sorted(ys)
        row_peaks = []
        if ys:
            curr_row = [ys[0]]
            for i in range(1, len(ys)):
                if ys[i] - ys[i-1] > 15:
                    row_peaks.append(np.mean(curr_row))
                    curr_row = [ys[i]]
                else:
                    curr_row.append(ys[i])
            row_peaks.append(np.mean(curr_row))
            
        # Map centers to the 5x10 grid
        reg_grid = [None] * 5
        for bx, by in centers:
            # Find closest col
            c_idx = np.argmin([abs(bx - p) for p in col_peaks])
            if c_idx >= 5: continue
            
            # Find closest row (digit) among the expected 10 rows
            # We use the relative position in Y
            digit = round((by - min(ys)) / ((max(ys) - min(ys)) / 9)) if max(ys) > min(ys) else 0
            if 0 <= digit <= 9:
                reg_grid[c_idx] = str(digit)
                
        return "".join([d for d in reg_grid if d is not None])

    def _process_card_v2(self, image: np.ndarray, bubbles: List[Any]) -> Dict[str, Any]:
        """Process card by targeting every bubble position (ROI Sampling)."""
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Use adaptive threshold only to find candidate bubbles for GRID ALIGNMENT
        centers = [(x + w_b/2, y + h_b/2) for (x, y, w_b, h_b) in bubbles]
        reg_centers = [c for c in centers if c[0] < w * 0.25]
        
        # 2. Extract registration params
        reg_id, params = self._extract_registration_and_params(reg_centers, h, w)
        if not params:
            return {"registration": "", "answers": {}}

        # 3. Sample every question bubble position
        answers = {}
        y0, dy = params["y_start"], params["y_step"]
        x0, dx = params["x_start"], params["x_step"]
        block_offsets = [7.5, 11.0, 14.5, 18.2]
        
        roi_size = 12 # Half-size of bubble ROI
        
        for g_idx, b_off in enumerate(block_offsets):
            for r_idx in range(10):
                q_num = g_idx * 10 + r_idx + 1
                for c_idx in range(5):
                    # Target coordinates
                    tx = int(x0 + (b_off + c_idx * 0.5) * dx)
                    ty = int(y0 + r_idx * dy)
                    
                    # Prevent out of bounds
                    y1, y2 = max(0, ty - roi_size), min(h, ty + roi_size)
                    x1, x2 = max(0, tx - roi_size), min(w, tx + roi_size)
                    
                    roi = gray[y1:y2, x1:x2]
                    if roi.size == 0: continue
                    
                    # FINAL CALIBRATION: Threshold 180 ensures only dark marks are caught.
                    # Empty circles average ~213-230.
                    if np.mean(roi) < 180:
                        if q_num not in answers: answers[int(q_num)] = []
                        answers[int(q_num)].append(int(c_idx + 1))
                        
        return {"registration": reg_id, "answers": answers}

    def _extract_registration_and_params(self, centers: List[tuple], h: int, w: int) -> tuple:
        if not centers: return "", None
        xs = sorted([c[0] for c in centers])
        col_peaks = []
        if xs:
            curr = [xs[0]]
            for i in range(1, len(xs)):
                if xs[i] - xs[i-1] > 20:
                    col_peaks.append(np.mean(curr))
                    curr = [xs[i]]
                else: curr.append(xs[i])
            col_peaks.append(np.mean(curr))
        
        if len(col_peaks) < 2: return "", None
        
        ys = sorted([c[1] for c in centers])
        row_peaks = []
        if ys:
            curr = [ys[0]]
            for i in range(1, len(ys)):
                if ys[i] - ys[i-1] > 15:
                    row_peaks.append(np.mean(curr))
                    curr = [ys[i]]
                else: curr.append(ys[i])
            row_peaks.append(np.mean(curr))
            
        if len(row_peaks) < 2: return "", None
        
        # Calculate steps
        x_step = (max(col_peaks) - min(col_peaks)) / (len(col_peaks) - 1)
        y_step = (max(row_peaks) - min(row_peaks)) / (len(row_peaks) - 1)
        
        params = {
            "x_start": min(col_peaks), "x_step": x_step,
            "y_start": min(row_peaks), "y_step": y_step
        }
        
        # Extract ID
        reg_id = ""
        for cp in col_peaks[:5]:
            best_digit = None
            min_d = 999
            for bx, by in centers:
                if abs(bx - cp) < 15:
                    digit = round((by - params["y_start"]) / params["y_step"])
                    if 0 <= digit <= 9:
                        dist = abs((by - params["y_start"]) - digit * params["y_step"])
                        if dist < min_d:
                            min_d = dist
                            best_digit = digit
            if best_digit is not None: reg_id += str(best_digit)
            
        return reg_id, params

    def _extract_questions_anchored(self, centers: List[tuple], params: dict, h: int, w: int) -> Dict[int, List[int]]:
        answers = {}
        # Geometric layout of Ye-dam OMR:
        # Distance from Reg column 1 to Question Block 1 choice 1 is ~8.5x Reg X step
        # Question rows are aligned with Reg rows
        
        x0, dx = params["x_start"], params["x_step"]
        y0, dy = params["y_start"], params["y_step"]
        
        # These offsets are relative to Reg grid
        # Block 1 starts at ~7.5x, Block 2 at ~11x, etc.
        # Adjusted offsets based on visual grid verification
        block_offsets = [7.5, 11.0, 14.5, 18.2] # Fine-tuned block 4 offset
        choice_step = 0.5 * dx
        
        for bx, by in centers:
            if bx < x0 + 6 * dx: continue # Skip registration area
            
            # Find row
            r_idx = round((by - y0) / dy)
            if not (0 <= r_idx < 10): continue
            
            # Find block
            rel_x = (bx - x0) / dx
            g_idx = -1
            for i, offset in enumerate(block_offsets):
                if offset - 1.5 <= rel_x <= offset + 3.5:
                    g_idx = i
                    break
            if g_idx == -1: continue
            
            q_num = g_idx * 10 + r_idx + 1
            # Choice within block
            choice = round((rel_x - block_offsets[g_idx]) / 0.5) + 1
            if 1 <= choice <= 5:
                q_key = int(q_num)
                if q_key not in answers: answers[q_key] = []
                answers[q_key].append(int(choice))
                
        return {int(q): sorted(list(set(ans))) for q, ans in answers.items()}

    def _extract_questions_auto(self, centers: List[tuple], h: int, w: int) -> Dict[int, List[int]]:
        """Fallback auto-fit logic."""
        if not centers: return {}
        xs = sorted([c[0] for c in centers])
        group_boundaries = []
        if xs:
            start = xs[0]
            for i in range(1, len(xs)):
                if xs[i] - xs[i-1] > 100:
                    group_boundaries.append((start - 10, xs[i-1] + 10))
                    start = xs[i]
            group_boundaries.append((start - 10, xs[-1] + 10))
            
        ys = sorted([c[1] for c in centers])
        row_peaks = []
        if ys:
            curr = [ys[0]]
            for i in range(1, len(ys)):
                if ys[i] - ys[i-1] > 30: 
                    row_peaks.append(np.mean(curr))
                    curr = [ys[i]]
                else: curr.append(ys[i])
            row_peaks.append(np.mean(curr))
            
        answers = {}
        for g_idx, (g_x1, g_x2) in enumerate(group_boundaries[:4]):
            g_centers = [c for c in centers if g_x1 <= c[0] <= g_x2]
            if not g_centers: continue
            g_xs = sorted([c[0] for c in g_centers])
            col_peaks = []
            if g_xs:
                curr = [g_xs[0]]
                for i in range(1, len(g_xs)):
                    if g_xs[i] - g_xs[i-1] > 15:
                        col_peaks.append(np.mean(curr))
                        curr = [g_xs[i]]
                    else: curr.append(g_xs[i])
                col_peaks.append(np.mean(curr))
            
            for bx, by in g_centers:
                if not col_peaks: continue
                c_idx = np.argmin([abs(bx - p) for p in col_peaks])
                if c_idx >= 5: continue
                if not row_peaks: continue
                r_idx = np.argmin([abs(by - p) for p in row_peaks])
                if r_idx >= 10: continue
                q_num = g_idx * 10 + r_idx + 1
                q_key = int(q_num)
                if q_key not in answers: answers[q_key] = []
                answers[q_key].append(int(c_idx + 1))
        return {int(q): sorted(list(set(ans))) for q, ans in answers.items()}

    def _detect_bubbles_adaptive(self, image: np.ndarray) -> List[Any]:
        """Custom bubble detection using optimized adaptive thresholding (C=15)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Optimized C=15 based on benchmark_sensitivity.py
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 21, 15)
        
        # Morphology to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bubbles = []
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if 10 <= w <= 100 and 10 <= h <= 100 and 0.7 <= ar <= 1.3:
                bubbles.append((x, y, w, h))
        return bubbles

    def _cluster_cards(self, bubbles: List[Any]) -> List[List[Any]]:
        """Cluster all detected bubbles into 3 groups corresponding to cards."""
        if not bubbles: return []
        
        # Sort by Y
        sorted_bubbles = sorted(bubbles, key=lambda b: b[1])
        
        # Find gaps in Y
        gaps = []
        for i in range(1, len(sorted_bubbles)):
            gap = sorted_bubbles[i][1] - (sorted_bubbles[i-1][1] + sorted_bubbles[i-1][3])
            if gap > 100: # Significant vertical gap between cards
                gaps.append(i)
                
        # We expect 2 gaps for 3 cards. If we find more/less, we try to split by count.
        if len(gaps) == 2:
            return [
                sorted_bubbles[:gaps[0]],
                sorted_bubbles[gaps[0]:gaps[1]],
                sorted_bubbles[gaps[1]:]
            ]
        
        # Fallback: Split by count if gaps are not clear
        n = len(sorted_bubbles)
        return [
            sorted_bubbles[:n//3],
            sorted_bubbles[n//3:2*n//3],
            sorted_bubbles[2*n//3:]
        ]

    def _process_card(self, image: np.ndarray, bubbles: List[Any]) -> Dict[str, Any]:
        """Establish grid from bubbles and fallback to fixed offsets."""
        h, w = image.shape[:2]
        
        # 1. Registration Sections (Fixed Offsets as fallback)
        # Expected X: 100-300
        reg_id = self._extract_registration_fixed(image)
        
        # 2. Question Sections (Fixed Offsets as fallback)
        # 4 blocks of 10 questions
        answers = self._extract_questions_fixed(image)
        
        return {
            "registration": reg_id,
            "answers": answers
        }

    def _extract_registration_fixed(self, image: np.ndarray) -> str:
        h, w = image.shape[:2]
        # Registration columns (Roughly 5 columns starting at 5% width)
        reg_id = ""
        # 5 columns of 10 digits
        start_x = int(w * 0.04)
        col_w = int(w * 0.02)
        start_y = int(h * 0.3)
        row_h = int(h * 0.05)
        
        for c in range(5):
            cx = start_x + c * col_w * 2.5
            digits = []
            for r in range(10):
                ry = start_y + r * row_h
                # Check mark at (cx, ry)
                roi = image[int(ry-10):int(ry+10), int(cx-10):int(cx+10)]
                if roi.size == 0: continue
                avg = np.mean(roi)
                if avg < 180: # Dark enough
                    digits.append(str(r))
            if digits: reg_id += digits[0]
        return reg_id

    def _extract_questions_fixed(self, image: np.ndarray) -> Dict[int, List[int]]:
        h, w = image.shape[:2]
        answers = {}
        # 4 Columns starting at 35% width
        col_group_start = [0.35, 0.50, 0.65, 0.80]
        row_start = 0.2
        row_step = 0.07
        
        for g_idx, start_pct in enumerate(col_group_start):
            gx = int(w * start_pct)
            for r_idx in range(10):
                q_num = g_idx * 10 + r_idx + 1
                ry = int(h * (row_start + r_idx * row_step))
                
                marked = []
                for choice in range(5):
                    bx = gx + choice * int(w * 0.02)
                    roi = image[ry-10:ry+10, bx-10:bx+10]
                    if roi.size == 0: continue
                    if np.mean(roi) < 180:
                        marked.append(choice + 1)
                if marked:
                    answers[q_num] = marked
        return answers
