import cv2
import numpy as np

class DocumentProcessor:
    def __init__(self):
        pass

    def resize_image(self, image, height=1000):
        """Resize image to a fixed height while maintaining aspect ratio."""
        ratio = height / image.shape[0]
        dim = (int(image.shape[1] * ratio), height)
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA), ratio

    def get_corners(self, image):
        """Detect the four corners of a page/card."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use multiple thresholding methods for robustness
        # 1. Canny
        edged = cv2.Canny(blurred, 50, 200)
        # 2. Otsu (for blocky shapes)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        combined = cv2.bitwise_or(edged, thresh)
        # Morphological operations to close gaps in contours
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(combined, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # Look for a 4-point contour that covers a significant area
            if len(approx) == 4 and cv2.contourArea(c) > (image.shape[0] * image.shape[1] * 0.1):
                return approx

        return None

    def order_points(self, pts):
        """Order points as: top-left, top-right, bottom-right, bottom-left."""
        rect = np.zeros((4, 2), dtype="float32")
        pts = pts.reshape(4, 2)

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def four_point_transform(self, image, pts):
        """Apply perspective transform to get a top-down view."""
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped

    def process_document(self, image_path):
        """Main method to load, detect corners, and warp a document."""
        image = cv2.imread(image_path)
        if image is None:
            return None

        # Resize for faster processing while keeping track of the ratio
        resized, ratio = self.resize_image(image)
        
        corners = self.get_corners(resized)
        if corners is None:
            # Fallback if no 4-point contour found - return original
            return image

        # Rescale corners back to original image size
        scaled_corners = (corners.reshape(4, 2) / ratio).astype("float32")
        
        warped = self.four_point_transform(image, scaled_corners)
        return warped

if __name__ == "__main__":
    # Test code (if you have an image)
    # processor = DocumentProcessor()
    # warped = processor.process_document("sample.jpg")
    # cv2.imwrite("warped.jpg", warped)
    pass
