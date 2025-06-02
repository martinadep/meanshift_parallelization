import argparse
import numpy as np
import pandas as pd
from PIL import Image
from skimage import color  # per conversione LAB
from config import in_img_path, original_csv_path

def image_to_csv(input_img_path, output_csv_path):
    # Load the image
    image = Image.open(input_img_path)
    image = image.convert("RGB")
    width, height = image.size

    # Convert image to LAB
    rgb_image = np.array(image) / 255.0  # Normalize to [0, 1]
    lab_image = color.rgb2lab(rgb_image)

    # Flatten the pixels (L, A, B)
    pixels = lab_image.reshape(-1, 3)

    # Prepare the data to be written to the CSV
    data = [
        ["width", "height"],  # First row
        [width, height],
        ["L", "A", "B"]  # Pixel header
    ]
    data.extend(pixels.tolist())  # Add pixel data

    # Save the data to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False, header=False)

    # Print the result
    print(f"\"{input_img_path}\" converted in LAB at \"{output_csv_path}\" - size: {width}x{height}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert image to CSV (LAB color space).")

    # Argument for input image path
    parser.add_argument(
        '--input', '-i',
        type=str,
        default=in_img_path,
        help=f"Path to the input image (default: {in_img_path})"
    )

    # Argument for output CSV file path
    parser.add_argument(
        '--output', '--csv', '-o',
        type=str,
        default=original_csv_path,
        help=f"Path to save the output CSV (default: {original_csv_path})"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the user-provided or default paths
    image_to_csv(args.input, args.output)

if __name__ == "__main__":
    main()
