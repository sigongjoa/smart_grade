import cv2
import pytest
from pytest_bdd import scenario, given, when, then
from backend.engine.yedam_grader import YeDamGrader

@scenario('../features/omr_grading.feature', 'Successful card isolation from full page')
def test_isolation():
    pass

@scenario('../features/omr_grading.feature', 'Accurate question extraction for Card 1')
def test_grading_accuracy():
    pass

@given('a full page OMR image "scan_20260212_160120.jpg"', target_fixture="full_image")
def full_image():
    path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    img = cv2.imread(path)
    assert img is not None
    return img

@when('the image is processed by YeDamGrader', target_fixture="grading_results")
def grading_results(full_image):
    grader = YeDamGrader()
    return grader.process_page(full_image)

@then('exactly 3 cards should be isolated')
def check_card_count(grading_results):
    assert len(grading_results) == 3

@given('the sample OMR image', target_fixture="sample_results")
def sample_results():
    path = "/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg"
    img = cv2.imread(path)
    grader = YeDamGrader()
    return grader.process_page(img)

@when('Card 1 is graded', target_fixture="card_1_data")
def card_1_data(sample_results):
    # Retrieve the result for the second card (index 1)
    return sample_results[1]

@then('Question 1 answer should be extracted correctly')
def check_q1(card_1_data):
    # Based on our previous verification, Q1 in Card 1 had [2]
    # Adjust expectations based on actual markings if needed
    assert 1 in card_1_data["answers"]
    assert card_1_data["answers"][1] == [2]

@then('Question 5 answer should be extracted correctly')
def check_q5(card_1_data):
    assert 5 in card_1_data["answers"]
    assert card_1_data["answers"][5] == [2]
