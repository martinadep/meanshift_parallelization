import numpy as np
import pandas as pd
from PIL import Image

from config import modified_csv_path, out_img_path

# Leggi la dimensione originale
#with open("size.txt", "r") as f:
#    width, height = map(int, f.read().split(","))

# read csv
df = pd.read_csv(modified_csv_path, header=None)
#print(df.head())
print(df.iloc[3:].drop_duplicates())  # Dovresti vedere solo 4 righe uniche

width, height = int(df.iloc[1,0],), int(df.iloc[1,1])

# pixel starts from fourth row
rgb_values = df.iloc[3:].values
rgb_array = np.array(rgb_values, dtype=np.uint8)
rgb_array = rgb_array.reshape((height, width, 3))

# create image
img = Image.fromarray(rgb_array, "RGB")
img.save(out_img_path)
img.show()
print(f"Image saved as \"{out_img_path}\"")
