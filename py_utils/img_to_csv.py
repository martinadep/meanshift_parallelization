import argparse
import numpy as np
import pandas as pd
from PIL import Image
from config import in_img_path, original_csv_path

def image_to_csv(input_img_path, output_csv_path):
    # Load the image
    image = Image.open(input_img_path)
    image = image.convert("RGB")
    width, height = image.size

    # Flatten the pixels (R, G, B)
    pixels = np.array(image).reshape(-1, 3)

    # Prepare the data to be written to the CSV
    data = [
        ["width", "height"],  # First row
        [width, height],
        ["R", "G", "B"]  # Pixel header
    ]
    data.extend(pixels.tolist())  # Add pixel data

    # Save the data to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False, header=False)

    # Print the result
    print(f"\"{input_img_path}\" converted in \"{output_csv_path}\" - size: {width}x{height}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert image to CSV.")

    # Argument for input image path
    parser.add_argument(
        '--input', '-i',
        type=str,
        default=in_img_path,  # Default value from config.py
        help=f"Path to the input image (default: {in_img_path})"
    )

    # Argument for output CSV file path
    parser.add_argument(
        '--output', '--csv', '-o',
        type=str,
        default=original_csv_path,  # Default value from config.py
        help=f"Path to save the output CSV (default: {original_csv_path})"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the user-provided or default paths
    image_to_csv(args.input, args.output)

if __name__ == "__main__":
    main()
