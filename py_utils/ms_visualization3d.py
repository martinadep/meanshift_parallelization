import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans

from config import LANDSCAPE_INCHES

# Seed per riproducibilità
np.random.seed(42)
n_points = 3000

# ----------------------------
# Cluster 3D personalizzati
# ----------------------------
# 1. Primo piano: grande e piatto, più alto e più a sinistra
x1 = np.random.normal(10, 20, n_points//7) 
y1 = np.random.normal(30, 20, n_points//7) 

x2 = np.random.normal(10, 25, n_points//3) 
y2 = np.random.normal(150, 25, n_points//3) 

x3 = np.random.normal(90, 15, n_points//8) 
y3 = np.random.normal(100, 15, n_points//8) 

x4 = np.random.normal(60, 15, n_points//10)  
y4 = np.random.normal(90, 15, n_points//10)  

x5 = np.random.normal(100, 25, n_points//6)   
y5 = np.random.normal(10, 25, n_points//6)  

x = np.concatenate([x1, x2, x3, x4, x5])
y = np.concatenate([y1, y2, y3, y4, y5])

# Clustering per colorare i punti
points = np.vstack((x, y)).T
kmeans = KMeans(n_clusters=4, random_state=42)
labels = kmeans.fit_predict(points)

# Stima della densità con KDE
xy = np.vstack([x, y])
kde = gaussian_kde(xy)

# Griglia di valutazione
xmin, xmax = x.min()-5, x.max()+5
ymin, ymax = y.min()-5, y.max()+5
xx, yy = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]
pos = np.vstack([xx.ravel(), yy.ravel()])
zz = np.reshape(kde(pos).T, xx.shape)

# Figura con tre sottografi
fig = plt.figure(figsize=(18,6), facecolor='white')

# Grafico 2D (punti neri)
ax1 = fig.add_subplot(1,3,1)
ax1.set_facecolor('white')
ax1.scatter(x, y, s=4, c='black', alpha=0.6)
# Ingrandisci il font dei tick
ax1.tick_params(axis='both', labelsize=16)
# ax1.set_title("(a) 2D sample distribution", fontsize=12)

# Grafico 2D con cluster colorati
ax2 = fig.add_subplot(1,3,2)
ax2.set_facecolor('white')
ax2.scatter(x, y, s=4, c=labels, cmap='tab10', alpha=0.6)
# Ingrandisci il font dei tick
ax2.tick_params(axis='both', labelsize=16)
# ax2.set_title("(b) clustered 2D sample", fontsize=12)

# Grafico 3D (colline di densità)
ax3 = fig.add_subplot(1,3,3, projection='3d')
surf = ax3.plot_surface(xx, yy, zz, cmap=plt.cm.jet, linewidth=0, antialiased=True)
# Ingrandisci il font dei tick
ax3.tick_params(axis='both', labelsize=16)
# ax3.set_title("(c) Kernel Density Estimation", fontsize=15)
cbar = fig.colorbar(surf, ax=ax3, shrink=0.6, aspect=10)
cbar.set_label("Normalized density", fontsize=18)
plt.tight_layout()
plt.savefig("ms_visualization3d.png", dpi=300)
print("3D visualization saved as ms_visualization3d.png")
plt.show()
