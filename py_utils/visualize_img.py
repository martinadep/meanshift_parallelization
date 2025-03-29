import numpy as np
import pandas as pd
from PIL import Image

# Leggi la dimensione originale
with open("size.txt", "r") as f:
    width, height = map(int, f.read().split(","))

# Carica il CSV
#df = pd.read_csv("output.csv")
df = pd.read_csv("../reconstructed.csv")
# Converti in array NumPy e ricostruisci l'immagine
pixels = df.to_numpy().reshape((height, width, 3))
image = Image.fromarray(pixels.astype(np.uint8))  # Converti in immagine

# Mostra e salva l'immagine
image.show()
image.save("reconstructed.jpg")

print("Immagine ricostruita salvata come 'reconstructed.jpg'")
