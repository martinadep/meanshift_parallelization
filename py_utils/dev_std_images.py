import os
import csv
import numpy as np
import glob
from scipy.stats import entropy
from scipy.ndimage import sobel
import matplotlib.pyplot as plt  # <-- aggiunto


def analyze_lab_csv(csv_path):
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Leggi width, height
    width, height = None, None
    for i, row in enumerate(rows):
        if row and row[0].strip().lower() == 'width':
            width = int(rows[i+1][0])
            height = int(rows[i+1][1])
        if row and row[0].strip() == 'L':
            data_start = i + 1
            break
    else:
        return None

    # Estrai i dati numerici
    data = []
    for row in rows[data_start:]:
        if len(row) >= 3:
            try:
                data.append([float(row[0]), float(row[1]), float(row[2])])
            except ValueError:
                continue

    if not data:
        return None

    arr = np.array(data)
    means = np.mean(arr, axis=0)
    stds = np.std(arr, axis=0)

    # Ricostruisci immagine 2D (canale L)
    if width is not None and height is not None:
        try:
            L = arr[:,0].reshape((height, width))
        except Exception:
            L = arr[:,0]  # fallback monodimensionale
    else:
        L = arr[:,0]

    # Entropia sul canale L
    hist, _ = np.histogram(L, bins=256, density=True)
    ent = entropy(hist + 1e-12)

    # Varianza del gradiente sul canale L
    if L.ndim == 2:
        gx = sobel(L, axis=1)
        gy = sobel(L, axis=0)
        grad_mag = np.hypot(gx, gy)
        grad_var = np.var(grad_mag)

        # Edge Density: percentuale di pixel sopra soglia
        thresh = np.mean(grad_mag) + np.std(grad_mag)
        edge_density = np.sum(grad_mag > thresh) / grad_mag.size
    else:
        grad_var = np.nan
        edge_density = np.nan

    return means, stds, ent, grad_var, edge_density

def main():
    batch_dir = 'data/batch'
    csv_files = glob.glob(os.path.join(batch_dir, 'original_*.csv'))
    results = []
    print(f"{'Immagine':<20} {'Mean L':<8} {'Std L':<8} {'Entropia':<10} {'GradVar':<10} {'EdgeDens':<10}")
    print('-'*80)
    for csv_path in sorted(csv_files):
        result = analyze_lab_csv(csv_path)
        img_name = os.path.basename(csv_path)
        if result:
            means, stds, ent, grad_var, edge_density = result
            print(f"{img_name:<20} {means[0]:<8.2f} {stds[0]:<8.2f} {ent:<10.3f} {grad_var:<10.3f} {edge_density:<10.3f}")
            results.append((img_name, edge_density))
        else:
            print(f"{img_name:<20} {'-':<8} {'-':<8} {'-':<10} {'-':<10} {'-':<10}")

    # Visualizza edge density
    if results:
        img_names = [r[0] for r in results]
        edge_densities = [r[1] for r in results]
        plt.figure(figsize=(10,5))
        plt.plot(img_names, edge_densities, marker='o')
        plt.xticks(rotation=90)
        plt.ylabel('Edge Density')
        plt.xlabel('Immagine')
        plt.title('Edge Density per Immagine')
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    main()