from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
import cv2
import numpy as np
import traceback
from engine.document_processor import DocumentProcessor
from engine.bubble_detector import BubbleDetector
from engine.ocr_engine import OCREngine
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"

app = FastAPI(title="Smart-Grader API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Mount static files to serve processed images
app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")

# Initialize engines
doc_processor = DocumentProcessor()
bubble_detector = BubbleDetector()
ocr_engine = OCREngine()

@app.post("/api/grade")
async def grade_omr(file: UploadFile = File(...)):
    """
    Upload an OMR scan and get grading results.
    """
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. Processing (Alignment)
        warped = doc_processor.process_document(input_path)
        if warped is None:
            raise HTTPException(status_code=400, detail="Could not detect document corners.")
            
        warped_path = os.path.join(PROCESSED_DIR, f"warped_{file_id}.jpg")
        
        # 2. Bubble Detection & Grading
        bubbles = bubble_detector.detect_bubbles(warped)
        marking_results = bubble_detector.check_marking(warped, bubbles)
        
        # Visualize detections on warped image
        vis_image = warped.copy()
        for i, res in enumerate(marking_results):
            x, y, w, h = res["bbox"]
            color = (0, 255, 0) if res["is_marked"] else (0, 0, 255)
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
            
        cv2.imwrite(warped_path, vis_image)
        
        # Multi-column mapping logic for SS-03
        # 1. Sort by X to find columns
        columns = bubble_detector.detect_columns(bubbles, col_threshold=60)
        
        grading_results = {}
        # Filter out the first few columns if they are part of Class/ID info
        # For SS-03, typically columns starting from X > 300 are questions
        question_columns = [col for col in columns if col[0][0] > 300]
        
        # Process each question column (Expected 4 columns of 10 questions)
        for col_idx, col_bubbles in enumerate(question_columns[:4]):
            grid_rows = bubble_detector.sort_into_grid(col_bubbles)
            for row_idx, row in enumerate(grid_rows):
                q_num = col_idx * 10 + row_idx + 1
                marking_status = bubble_detector.check_marking(warped, row)
                marked_indices = [idx for idx, r in enumerate(marking_status) if r["is_marked"]]
                grading_results[q_num] = {"selected": marked_indices, "confidence": [r["score"] for r in marking_status]}
        
        # 3. Handwriting OCR (optional for name)
        text_results = ocr_engine.extract_text(warped)
        
        # Improved name extraction logic
        student_name = "Unknown"
        all_texts = [res["text"] for res in text_results]
        
        for i, text in enumerate(all_texts):
            if "이름" in text or "성명" in text:
                # Often the name is in the same block or the next one
                # If "이름: 김철수" format
                if ":" in text and len(text.split(":")[1].strip()) > 0:
                    student_name = text.split(":")[1].strip()
                elif i + 1 < len(all_texts):
                    student_name = all_texts[i+1]
                break
        
        # 4. Final aggregation
        response = {
            "id": file_id,
            "warped_url": f"/processed/warped_{file_id}.jpg",
            "grades": grading_results,
            "text_found": text_results,
            "student_name": student_name,
            "message": "Grading complete."
        }
        
        return response
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Smart-Grader API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
