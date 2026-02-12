
import cv2
import numpy as np

def compare_preprocessing(image_path, output_dir):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return

    # 1. Global Threshold (Current)
    _, global_th = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)
    
    # 2. Adaptive Threshold (Mean)
    adaptive_mean = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                          cv2.THRESH_BINARY_INV, 21, 10)
    
    # 3. Adaptive Threshold (Gaussian)
    adaptive_gauss = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 21, 10)

    # 4. Denoised Global
    denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    _, denoised_th = cv2.threshold(denoised, 180, 255, cv2.THRESH_BINARY_INV)

    # Save samples
    cv2.imwrite(f"{output_dir}/thresh_global.jpg", global_th[1000:1500, 1000:1500])
    cv2.imwrite(f"{output_dir}/thresh_adaptive_mean.jpg", adaptive_mean[1000:1500, 1000:1500])
    cv2.imwrite(f"{output_dir}/thresh_adaptive_gauss.jpg", adaptive_gauss[1000:1500, 1000:1500])
    cv2.imwrite(f"{output_dir}/thresh_denoised.jpg", denoised_th[1000:1500, 1000:1500])
    
    print("Preprocessing comparison samples saved.")

if __name__ == "__main__":
    compare_preprocessing("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", ".")
