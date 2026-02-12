import pytest
import numpy as np
import cv2
import os
import sys

# Add root directory to sys.path for engine imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.engine.yedam_grader import YeDamGrader
from backend.engine.bubble_detector import BubbleDetector

@pytest.fixture
def sample_image_path():
    return "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"

@pytest.fixture
def yedam_grader():
    return YeDamGrader()

@pytest.fixture
def mock_bubbles():
    """Returns a list of bubbles simulated for Card 0 Layout."""
    bubbles = []
    # Mock registration bubbles (5 columns of 10)
    for c in range(5):
        for r in range(10):
            bubbles.append((100 + c*50, 500 + r*100, 20, 20, 1.0))
            
    # Mock question bubbles (4 columns of 10 questions, 5 choices each)
    for col in range(4):
        for q in range(10):
            for choice in range(5):
                bubbles.append((800 + col*400 + choice*50, 400 + q*150, 20, 20, 1.0))
    return bubbles
