import argparse
import numpy as np
import pandas as pd
from PIL import Image
from skimage import color  # per conversione LAB
from config import in_img_path, original_csv_path


def image_to_csv(input_img_path, output_csv_path, resize=None):
    """
    Converte un'immagine in CSV (spazio colore LAB), con resize opzionale.

    :param input_img_path: Path immagine input
    :param output_csv_path: Path CSV di output
    :param resize: tuple (width, height) oppure None per mantenere dimensioni originali
    """

    image = Image.open(input_img_path).convert("RGB")
    if resize is not None:
        image = image.resize(resize, Image.LANCZOS)

    width, height = image.size

    # Convert image to LAB
    rgb_image = np.array(image) / 255.0  # Normalize to [0, 1]
    lab_image = color.rgb2lab(rgb_image)

    # Flatten the pixels (L, A, B)
    pixels = lab_image.reshape(-1, 3)

    data = [
        ["width", "height"],
        [width, height],
        ["L", "A", "B"]  
    ]
    data.extend(pixels.tolist())  # Add pixel data

    # Save the data to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False, header=False)

    print(f"\"{input_img_path}\" converted to LAB at \"{output_csv_path}\" - size: {width}x{height}")


def main():
    parser = argparse.ArgumentParser(description="Convert image to CSV (LAB color space) with optional resize.")

    parser.add_argument(
        '--input', '-i',
        type=str,
        default=in_img_path,
        help=f"Path to the input image (default: {in_img_path})"
    )
    parser.add_argument(
        '--output', '--csv', '-o',
        type=str,
        default=original_csv_path,
        help=f"Path to save the output CSV (default: {original_csv_path})"
    )
    # 90x60 or 128x85
    parser.add_argument(
        '--resize', '-r',
        type=int,
        nargs=2,
        metavar=('WIDTH', 'HEIGHT'),
        help="Resize image to WIDTH HEIGHT before processing (default: original size)"
    )

    args = parser.parse_args()
    
    # if args.input == in_img_path and args.resize is None:
    #     resize = (90, 60)
    # else:
    resize = tuple(args.resize) if args.resize else None

    image_to_csv(args.input, args.output, resize)


if __name__ == "__main__":
    main()
