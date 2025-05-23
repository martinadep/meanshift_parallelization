import re
import numpy as np
import matplotlib.pyplot as plt
from config import metrics_path

def parse_perf_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    runs = content.strip().split('---')
    data = []
    for run in runs:
        if not run.strip():
            continue
        # Only parse if Bandwidth and Total Points are present
        if not re.search(r'Bandwidth:', run) or not re.search(r'Total Points:', run):
            continue
        try:
            d = {}
            d['Bandwidth'] = int(re.search(r'Bandwidth: (\d+)', run).group(1))
            d['Cluster Epsilon'] = float(re.search(r'Cluster Epsilon: ([\d.eE+-]+)', run).group(1))
            d['Iteration Epsilon'] = float(re.search(r'Iteration Epsilon: ([\d.eE+-]+)', run).group(1))
            d['DataType'] = re.search(r'DataType: (\w+)', run).group(1)
            d['Total Points'] = int(re.search(r'Total Points: (\d+)', run).group(1))
            d['Total Iterations'] = int(re.search(r'Total Iterations: (\d+)', run).group(1))
            d['Iterations/sec'] = float(re.search(r'Iterations/sec: ([\d.]+)', run).group(1))
            d['Elapsed Time'] = float(re.search(r'Elapsed Time: ([\d.]+)', run).group(1))
            d['Min Iterations'] = int(re.search(r'Min Iterations: (\d+)', run).group(1))
            d['Max Iterations'] = int(re.search(r'Max Iterations: (\d+)', run).group(1))
            d['Mean Iterations'] = float(re.search(r'Mean Iterations: ([\d.]+)', run).group(1))
            d['Stddev Iterations'] = float(re.search(r'Stddev Iterations: ([\d.]+)', run).group(1))
            iters = re.search(r'Iterations per point: ([\d\s]+)', run)
            d['Iterations per point'] = np.array([int(x) for x in iters.group(1).split()]) if iters else np.array([])
            data.append(d)
        except Exception as e:
            print(f"Skipping a run due to parse error: {e}")
            continue
    return data

def plot_histogram(data):
    plt.figure(figsize=(8,5))
    plt.hist(data['Iterations per point'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Histogram of Iterations per Point')
    plt.xlabel('Iterations')
    plt.ylabel('Count')
    plt.savefig('./data/histogram.png')
    plt.show()

def plot_iterations_per_sec(all_data):
    plt.figure(figsize=(8,5))
    plt.plot([i+1 for i in range(len(all_data))], [d['Iterations/sec'] for d in all_data], marker='o')
    plt.title('Iterations per Second over Runs')
    plt.xlabel('Run')
    plt.ylabel('Iterations/sec')
    plt.savefig('./data/iterations_per_sec.png')
    plt.show()

def plot_bar_stats(data):
    stats = [data['Min Iterations'], data['Max Iterations'], data['Mean Iterations'], data['Stddev Iterations']]
    labels = ['Min', 'Max', 'Mean', 'Stddev']
    plt.figure(figsize=(8,5))
    plt.bar(labels, stats, color=['green','red','blue','orange'])
    plt.title('Iteration Statistics')
    plt.ylabel('Iterations')
    plt.savefig('./data/iteration_stats.png')
    plt.show()

if __name__ == "__main__":
    all_data = parse_perf_file(metrics_path)
    # Plot for the last run
    plot_histogram(all_data[-1])
    plot_iterations_per_sec(all_data)
    plot_bar_stats(all_data[-1])