import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import matplotlib as mpl
from scipy.stats import gaussian_kde

# Generate a dataset with distinct clusters
def generate_data(n_samples=300, centers=3, std=1.0):
    np.random.seed(42)
    points = []
    for i in range(centers):
        center = np.random.uniform(-10, 10, size=(2,))
        cluster = np.random.randn(n_samples // centers, 2) * std + center
        points.append(cluster)
    return np.vstack(points)

# Gaussian Kernel function
def gaussian_kernel(distances, bandwidth):
    return np.exp(- (distances ** 2) / (2 * bandwidth ** 2))

# Mean-Shift Algorithm
def mean_shift(data, bandwidth=2.0, max_iter=50, tol=1e-3):
    points = data.copy()
    trajectories = [points.copy()]
    
    for _ in range(max_iter):
        new_points = []
        for point in points:
            distances = cdist([point], points)[0]
            weights = gaussian_kernel(distances, bandwidth)
            new_point = np.sum(points * weights[:, None], axis=0) / np.sum(weights)
            new_points.append(new_point)
        
        new_points = np.array(new_points)
        trajectories.append(new_points.copy())
        
        if np.linalg.norm(new_points - points) < tol:
            break
        
        points = new_points
    
    return points, trajectories

# Visualization with user interaction
def plot_evolution_interactive(data, trajectories):
    fig, ax = plt.subplots(figsize=(8, 6))
    index = [0]  # Mutable list to hold iteration index
    
    # Compute density for contour plot
    x, y = data[:, 0], data[:, 1]
    kde = gaussian_kde(np.vstack([x, y]))
    x_grid, y_grid = np.meshgrid(np.linspace(x.min()-1, x.max()+1, 100),
                                 np.linspace(y.min()-1, y.max()+1, 100))
    z_grid = kde(np.vstack([x_grid.ravel(), y_grid.ravel()])).reshape(x_grid.shape)
    
    def update_plot(event=None):
        if event:
            if event.key == 'right' and index[0] < len(trajectories) - 1:
                index[0] += 1
            elif event.key == 'left' and index[0] > 0:
                index[0] -= 1
        
        ax.clear()
        ax.contour(x_grid, y_grid, z_grid, levels=10, cmap='viridis', alpha=0.6)
        ax.scatter(data[:, 0], data[:, 1], color='gray', alpha=0.3, label='Original Data')
        if index[0] > 0:
            for j in range(len(data)):
                ax.plot([trajectories[index[0]-1][j, 0], trajectories[index[0]][j, 0]],
                        [trajectories[index[0]-1][j, 1], trajectories[index[0]][j, 1]],
                        'r-', alpha=0.5)
                ax.arrow(trajectories[index[0]-1][j, 0], trajectories[index[0]-1][j, 1],
                         (trajectories[index[0]][j, 0] - trajectories[index[0]-1][j, 0]) * 0.8,
                         (trajectories[index[0]][j, 1] - trajectories[index[0]-1][j, 1]) * 0.8,
                         head_width=0.2, head_length=0.2, fc='r', ec='r', alpha=0.7)
        ax.scatter(trajectories[index[0]][:, 0], trajectories[index[0]][:, 1], color='blue', label=f'Iteration {index[0]}')
        ax.set_title(f"Iteration {index[0]}")
        ax.legend()
        plt.draw()
    
    fig.canvas.mpl_connect('key_press_event', update_plot)
    update_plot(mpl.backend_bases.KeyEvent(name='key_press_event', canvas=fig.canvas, key='right'))  # Simulate right key event
    plt.show()

# Run the mean-shift clustering and visualize evolution
data = generate_data()
final_points, trajectories = mean_shift(data, bandwidth=2.0)
plot_evolution_interactive(data, trajectories)
