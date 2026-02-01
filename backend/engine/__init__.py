"""
Engine module for Smart-Grader OMR processing.

This module provides the core processing engines for:
- Document alignment and perspective correction
- Bubble detection and marking analysis
- OCR text extraction
"""

from .document_processor import DocumentProcessor, DocumentProcessorConfig
from .bubble_detector import BubbleDetector, BubbleDetectorConfig
from .ocr_engine import OCREngine

__all__ = [
    "DocumentProcessor",
    "DocumentProcessorConfig",
    "BubbleDetector",
    "BubbleDetectorConfig",
    "OCREngine",
]
