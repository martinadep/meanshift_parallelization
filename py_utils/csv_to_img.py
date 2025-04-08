import argparse
import numpy as np
import pandas as pd
from PIL import Image
from config import modified_csv_path, out_img_path

def csv_to_img(csv_path, output_img_path):
    # read csv
    df = pd.read_csv(csv_path, header=None)
    print("Clusters found:")
    print(df.iloc[3:].drop_duplicates())  # Print clusters

    width, height = int(df.iloc[1, 0]), int(df.iloc[1, 1])

    # pixel starts from fourth row
    rgb_values = df.iloc[3:].values
    rgb_array = np.array(rgb_values, dtype=np.uint8)
    rgb_array = rgb_array.reshape((height, width, 3))

    # create image
    img = Image.fromarray(rgb_array, "RGB")
    img.save(output_img_path)
    img.show()
    print(f"Image saved as \"{output_img_path}\"")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert CSV to image")

    # Argument for CSV file
    parser.add_argument(
        '--csv', '--input', '-i',
        type=str,
        default=modified_csv_path,  # Default to the path from config.py
        help=f"Path to the modified CSV (default: {modified_csv_path})"
    )

    # Argument for output image path
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=out_img_path,  # Default to the path from config.py
        help=f"Path to save the output image (default: {out_img_path})"
    )

    # Parse arguments
    args = parser.parse_args()

    # Call the function with the user-provided or default paths
    csv_to_img(args.csv, args.output)

if __name__ == "__main__":
    main()
