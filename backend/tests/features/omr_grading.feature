Feature: OMR Grading for Ye-dam Layout
    Specialized layout with 3 vertical cards per page.

    Scenario: Successful card isolation from full page
        Given a full page OMR image "scan_20260212_160120.jpg"
        When the image is processed by YeDamGrader
        Then exactly 3 cards should be isolated

    Scenario: Accurate question extraction for Card 1
        Given the sample OMR image
        When Card 1 is graded
        Then Question 1 answer should be extracted correctly
        And Question 5 answer should be extracted correctly
