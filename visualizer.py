import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import matplotlib as mpl
from scipy.stats import gaussian_kde
import argparse

def generate_data(n_samples=300, centers=3, std=1.0):
    np.random.seed(42)
    points = []
    for i in range(centers):
        center = np.random.uniform(-10, 10, size=(2,))
        cluster = np.random.randn(n_samples // centers, 2) * std + center
        points.append(cluster)
    return np.vstack(points)

def gaussian_kernel(distances, bandwidth):
    return np.exp(- (distances ** 2) / (2 * bandwidth))

def epanechnikov_kernel(distances, bandwidth):
    k = 0.75 * (1 - (distances / bandwidth) ** 2)
    k[distances > bandwidth] = 0
    return k

def mean_shift(data, bandwidth=2.0, max_iter=50, tol=1e-3, kernel='gaussian'):
    points = data.copy()
    trajectories = [points.copy()]
    
    kernel_function = gaussian_kernel if kernel == 'gaussian' else epanechnikov_kernel
    
    for _ in range(max_iter):
        new_points = []
        for point in points:
            distances = cdist([point], points)[0]
            weights = kernel_function(distances, bandwidth)
            new_point = np.sum(points * weights[:, None], axis=0) / np.sum(weights)
            new_points.append(new_point)
        
        new_points = np.array(new_points)
        trajectories.append(new_points.copy())
        
        if np.linalg.norm(new_points - points) < tol:
            break
        
        points = new_points
    
    return points, trajectories

def mean_shift_matrix(data, bandwidth=2.0, max_iter=50, tol=1e-3, kernel='gaussian'):
    points = data.copy()
    trajectories = [points.copy()]
    
    for _ in range(max_iter):
        distances = cdist(points, points)
        print("DISTANCES")
        print(distances)
        kernel_function = gaussian_kernel if kernel == 'gaussian' else epanechnikov_kernel
        weights = kernel_function(distances, bandwidth)
        print("WEIGHTS")
        print(weights)
        
        W1 = np.sum(weights, axis=1, keepdims=True)
        print("W1")
        print(W1)
        new_points = (weights @ points) / W1
        print("NEW POINTS")
        print(new_points)
        
        trajectories.append(new_points.copy())
        
        if np.linalg.norm(new_points - points) < tol:
            break
        
        points = new_points
    
    return points, trajectories


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mean-Shift Clustering with Visualization")
    parser.add_argument('--bandwidth', '-b', type=float, default=2.0, help='Bandwidth for the kernel function')
    parser.add_argument('--max_iter', '-m', type=int, default=50, help='Maximum number of iterations')
    parser.add_argument('--tol', '-t', type=float, default=1e-3, help='Convergence tolerance')
    parser.add_argument('--kernel', '-k', type=str, choices=['gaussian', 'epanechnikov'], default='epanechnikov', help='Kernel function')
    parser.add_argument('--method', '-M', type=str, choices=['loop', 'matrix'], default='matrix', help='Mean-shift implementation method')
    parser.add_argument('--n_samples', '-n', type=int, default=300, help='Number of samples to generate')
    parser.add_argument('--centers', '-c', type=int, default=3, help='Number of centers for data generation')
    parser.add_argument('--std', '-s', type=float, default=1.0, help='Standard deviation for data generation')
    args = parser.parse_args()

    np.set_printoptions(precision=4, linewidth=200)
    data = generate_data(args.n_samples, args.centers, args.std)

    if args.method == 'loop':
        final_points, trajectories = mean_shift(data, bandwidth=args.bandwidth, max_iter=args.max_iter, tol=args.tol, kernel=args.kernel)
    else:
        final_points, trajectories = mean_shift_matrix(data, bandwidth=args.bandwidth, max_iter=args.max_iter, tol=args.tol, kernel=args.kernel)

    print('========================== final_points ==========================')
    print(final_points)
    print('========================== trajectories ==========================')
    for i in range(len(trajectories)):
        print(f'\nIteration {i}:')
        print(trajectories[i])

    plot_evolution_interactive(data, trajectories)
