
import cv2
import numpy as np
import matplotlib.pyplot as plt

def analyze_projections(image_path, output_dir):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return

    # Invert for projections
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 1. Vertical Projection (Sums of rows) - should show card separations
    v_proj = np.sum(thresh, axis=1)
    
    # 2. Horizontal Projection (Sums of columns) - should show column structures
    h_proj = np.sum(thresh, axis=0)

    # Plot and save
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(v_proj)
    plt.title("Vertical Projection (Row Sums)")
    plt.xlabel("Row index")
    plt.ylabel("Intensity sum")

    plt.subplot(2, 1, 2)
    plt.plot(h_proj)
    plt.title("Horizontal Projection (Column Sums)")
    plt.xlabel("Column index")
    plt.ylabel("Intensity sum")

    plt.tight_layout()
    plot_path = f"{output_dir}/layout_projections.png"
    plt.savefig(plot_path)
    print(f"Projection analysis saved to {plot_path}")

    # Find candidate card boundaries (large regions of low intensity)
    # We look for valleys in v_proj
    # Normalized valley search
    v_norm = v_proj / np.max(v_proj)
    valleys = np.where(v_norm < 0.05)[0] # Threshold for "empty space"
    
    # Group consecutive valleys
    if len(valleys) > 0:
        gap_starts = []
        if len(valleys) > 0:
            gap_starts.append(valleys[0])
            for i in range(1, len(valleys)):
                if valleys[i] - valleys[i-1] > 100: # Significant gap
                    gap_starts.append(valleys[i])
        print(f"Candidate gaps found at rows: {gap_starts}")

if __name__ == "__main__":
    analyze_projections("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg", ".")
