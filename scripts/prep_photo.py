import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Could not find: {input_path}")

    # Load image
    img = Image.open(input_path).convert("RGBA")

    # Remove background
    img_no_bg = remove(img)

    # Composite subject onto pure white background
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img_no_bg).convert("RGB")

    # Convert PIL -> OpenCV
    cv_img = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Boost local contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Save result
    Image.fromarray(enhanced).save(output_path)

    print(f"Saved prepared image to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    prep_photo(sys.argv[1])
