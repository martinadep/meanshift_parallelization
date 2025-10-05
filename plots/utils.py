import re
import numpy as np

# File reading utilities
def try_read_file(filepath):
    """Try different encodings"""
    encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try binary mode
    try:
        with open(filepath, 'rb') as file:
            return file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")
        return ""

# Data extraction functions
def extract_times(file_content, include_slic=True):
    """Extract execution times from file content."""
    # Extract both SLIC and mean shift times
    slic_times = re.findall(r'slic execution time: (\d+\.\d+)', file_content)
    mean_shift_times = re.findall(r'mean_shift execution time: (\d+\.\d+)', file_content)
    
    if not mean_shift_times:
        return []
    
    mean_shift_times = [float(time) for time in mean_shift_times]
    
    # For SLIC implementations, add the preprocessing time if requested
    if include_slic and slic_times and "slic" in file_content.lower():
        slic_times = [float(time) for time in slic_times]
        # Return combined times (SLIC + mean_shift)
        return [slic_times[i] + mean_shift_times[i] for i in range(min(len(slic_times), len(mean_shift_times)))]
    else:
        return mean_shift_times

def extract_separate_times(file_content):
    """Extract SLIC and mean shift times separately."""
    # Extract both SLIC and mean shift times
    slic_times = re.findall(r'slic execution time: (\d+\.\d+)', file_content)
    mean_shift_times = re.findall(r'mean_shift execution time: (\d+\.\d+)', file_content)
    
    if not mean_shift_times:
        return [], []
    
    # Convert to float
    mean_shift_times = [float(time) for time in mean_shift_times]
    
    # For SLIC implementations, return both times separately
    if slic_times and "slic" in file_content.lower():
        slic_times = [float(time) for time in slic_times]
        # Return both time arrays separately
        return slic_times[:len(mean_shift_times)], mean_shift_times
    else:
        # No SLIC times or not a SLIC implementation
        return [], mean_shift_times

def parse_perf_file(filename):
    """Parse performance metrics file for MeanShift."""
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