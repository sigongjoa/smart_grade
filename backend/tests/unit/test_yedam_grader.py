import pytest
import numpy as np
from backend.engine.yedam_grader import YeDamGrader

def test_cluster_cards_three_groups(yedam_grader):
    """Verify that bubbles are clustered into exactly 3 groups for a typical page."""
    # Create bubbles with large Y gaps to simulate 3 cards
    bubbles = []
    # Card 0
    for i in range(10): bubbles.append((100, 100 + i*10, 10, 10))
    # Card 1
    for i in range(10): bubbles.append((100, 500 + i*10, 10, 10))
    # Card 2
    for i in range(10): bubbles.append((100, 900 + i*10, 10, 10))
    
    clusters = yedam_grader._cluster_cards(bubbles)
    assert len(clusters) == 3
    assert len(clusters[0]) == 10
    assert len(clusters[1]) == 10
    assert len(clusters[2]) == 10

def test_process_card_empty_bubbles(yedam_grader):
    """Verify processing a card with no bubbles returns empty result."""
    # Use white image (no marks)
    res = yedam_grader._process_card(np.ones((1000, 1000, 3), dtype=np.uint8) * 255, [])
    assert res["registration"] == ""
    assert res["answers"] == {}

def test_registration_fixed_mapping(yedam_grader):
    """Verify registration extraction with simulated dark ROI."""
    # Create a white image
    img = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
    # Simulate a mark in column 0, row 5 (digit 5)
    start_x = int(1000 * 0.04)
    start_y = int(1000 * 0.3)
    ry = int(start_y + 5 * (1000 * 0.05))
    rx = int(start_x)
    # Larger mark to ensure mean < 180
    img[ry-8:ry+8, rx-8:rx+8] = 0 # Black mark
    
    reg_id = yedam_grader._extract_registration_fixed(img)
    assert len(reg_id) >= 1
    assert "5" in reg_id
