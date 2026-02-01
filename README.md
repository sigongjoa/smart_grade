# Smart-Grader AI

AI-based automatic grading system with flexible OMR recognition and LLM-powered analytics.

## Features
- **Flexible Vision OCR**: No timing marks required. Uses Homography for document alignment.
- **Hybrid Grading**: Combines pixel intensity analysis with AI verification.
- **Handwriting Recognition**: Uses PaddleOCR for short answers and student info.
- **Monthly Reports**: Automatic performance analysis using LLMs.

## Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python main.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Architecture
- **Vision Engine**: OpenCV + PaddleOCR
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite (Vanilla CSS)
- **Integration**: Mathesis-Synapse Node #13
