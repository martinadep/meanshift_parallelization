import numpy as np
import pandas as pd
from PIL import Image

# Carica l'immagine
image = Image.open("../dataset/flowers.jpg")
image = image.convert("RGB")  # Assicura che sia in formato RGB
width, height = image.size

# Converte in un array NumPy
pixels = np.array(image).reshape(-1, 3)  # Converti in lista di pixel (R,G,B)

# Salva il CSV
df = pd.DataFrame(pixels, columns=["R", "G", "B"])
df.to_csv("output.csv", index=False)

# Salva anche la dimensione dell'immagine
with open("size.txt", "w") as f:
    f.write(f"{width},{height}")

print(f"✅ Immagine salvata in output.csv - Dimensioni: {width}x{height}")
