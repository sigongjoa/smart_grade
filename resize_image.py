
import cv2
image = cv2.imread("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
if image is not None:
    small = cv2.resize(image, (1000, 1500))
    cv2.imwrite("/mnt/d/progress/mathesis/node13_smart_grader/scan_small.jpg", small)
    print("Saved scan_small.jpg")
else:
    print("Failed to load image")
