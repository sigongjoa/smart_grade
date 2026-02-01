from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import cv2
import logging
import aiofiles
from typing import Optional
from engine.document_processor import DocumentProcessor
from engine.bubble_detector import BubbleDetector
from engine.ocr_engine import OCREngine

os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart-Grader API")

# Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# SS-03 OMR Format Configuration
SS03_QUESTION_COLUMN_X_OFFSET = 300  # X coordinate threshold for question columns (skip ID columns)
SS03_COLUMN_THRESHOLD = 60  # Pixel threshold for grouping bubbles into columns
SS03_NUM_QUESTION_COLUMNS = 4  # Number of question columns in SS-03 format
SS03_QUESTIONS_PER_COLUMN = 10  # Questions per column

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Mount static files to serve processed images
app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")

# Initialize engines (OCR is lazy-loaded for faster startup)
doc_processor = DocumentProcessor()
bubble_detector = BubbleDetector()
_ocr_engine: Optional[OCREngine] = None


def get_ocr_engine() -> OCREngine:
    """Lazy initialization of OCR engine to improve startup time."""
    global _ocr_engine
    if _ocr_engine is None:
        logger.info("Initializing OCR engine (first use)...")
        _ocr_engine = OCREngine()
    return _ocr_engine


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file type and size."""
    # Check file extension
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file."
        )

@app.post("/api/grade")
async def grade_omr(file: UploadFile = File(...)):
    """
    Upload an OMR scan and get grading results.
    """
    # Validate file type
    validate_file(file)

    # Use only UUID for filename to prevent path traversal attacks
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or ".jpg")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    # Async file write for better performance
    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        async with aiofiles.open(input_path, "wb") as buffer:
            await buffer.write(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

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
        columns = bubble_detector.detect_columns(bubbles, col_threshold=SS03_COLUMN_THRESHOLD)

        grading_results = {}
        # Filter out the first few columns if they are part of Class/ID info
        # For SS-03, columns starting from X > threshold are questions
        question_columns = [
            col for col in columns if col[0][0] > SS03_QUESTION_COLUMN_X_OFFSET
        ]

        # Process each question column
        for col_idx, col_bubbles in enumerate(question_columns[:SS03_NUM_QUESTION_COLUMNS]):
            grid_rows = bubble_detector.sort_into_grid(col_bubbles)
            for row_idx, row in enumerate(grid_rows):
                q_num = col_idx * SS03_QUESTIONS_PER_COLUMN + row_idx + 1
                marking_status = bubble_detector.check_marking(warped, row)
                marked_indices = [
                    idx for idx, r in enumerate(marking_status) if r["is_marked"]
                ]
                grading_results[q_num] = {
                    "selected": marked_indices,
                    "confidence": [r["score"] for r in marking_status]
                }
        
        # 3. Handwriting OCR (optional for name) - lazy loaded
        ocr_engine = get_ocr_engine()
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
        
        # Clear grayscale cache to free memory
        bubble_detector.clear_cache()

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

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Grading error for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during grading. Please try again.")
    finally:
        # Clean up uploaded file to prevent disk space accumulation
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError as e:
                logger.warning(f"Failed to clean up file {input_path}: {e}")

@app.get("/")
async def root():
    return {"message": "Smart-Grader API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
