import numpy as np
import pandas as pd
from PIL import Image

from config import in_img_path, original_csv_path

# load image
image = Image.open(in_img_path)
image = image.convert("RGB")
width, height = image.size


pixels = np.array(image).reshape(-1, 3)  # flatten pixels (R,G,B)

data = [
    ["width", "height"],  # first line
    [width, height],
    ["R", "G", "B"] # pixel header
]
data.extend(pixels.tolist())  # add pixels

# save CSV
df = pd.DataFrame(data)
df.to_csv(original_csv_path, index=False, header=False)

# Salva anche la dimensione dell'immagine
#with open("size.txt", "w") as f:
#    f.write(f"{width},{height}")

print(f"\"{in_img_path}\" converted in \"{original_csv_path}\" - size: {width}x{height}")
