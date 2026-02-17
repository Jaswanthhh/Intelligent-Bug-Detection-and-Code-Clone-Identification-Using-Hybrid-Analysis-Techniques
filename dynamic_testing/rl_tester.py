"""
A minimal 'dynamic testing' module:
- For Python files: tries to execute `python <file>` several times with randomized environment variables and random stdin.
- Records if any run returns non-zero exit code or raises exception (anomaly).
This is a tiny placeholder for RL-based dynamic test generation.
"""

import subprocess
import os
import random
import string
import time

def random_bytes_string(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_python_file_with_random_inputs(filepath, runs=5, timeout=5):
    """
    Runs the python file multiple times. For each run, sets an env var RANDOM_INPUT
    to a random string and sends a small random stdin.
    Returns summary: {"path":..., "runs": runs, "anomalies": [...list of run indexes and errors...] }
    """
    anomalies = []
    for i in range(runs):
        env = os.environ.copy()
        env["RANDOM_INPUT"] = random_bytes_string(16)
        random_stdin = random_bytes_string(8).encode('utf-8')
        try:
            proc = subprocess.run(
                ["python", filepath],
                input=random_stdin,
                capture_output=True,
                env=env,
                timeout=timeout
            )
            if proc.returncode != 0:
                anomalies.append({
                    "run": i,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout.decode('utf-8', errors='ignore')[:1000],
                    "stderr": proc.stderr.decode('utf-8', errors='ignore')[:1000]
                })
        except subprocess.TimeoutExpired as te:
            anomalies.append({"run": i, "timeout": True, "error": str(te)})
        except Exception as e:
            anomalies.append({"run": i, "error": str(e)})
    return {"path": filepath, "runs": runs, "anomalies": anomalies}

def scan_folder_dynamic(folder, runs_per_file=5, timeout=5, show_progress=False, file_extensions=None):
    results = []
    # Collect all Python files first (or specified extensions)
    if file_extensions is None:
        file_extensions = [".py"]
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    all_files = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if any(fn.endswith(ext) for ext in file_extensions):
                all_files.append(os.path.join(root, fn))
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Dynamic testing", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        try:
            res = run_python_file_with_random_inputs(path, runs=runs_per_file, timeout=timeout)
            results.append(res)
        except Exception as e:
            results.append({"path": path, "error": str(e)})
    return results

def scan_paths_dynamic(paths, runs_per_file=5, timeout=5, show_progress=False, file_extensions=None):
    """
    Scan list of paths (files or folders) and run dynamic tests.
    """
    results = []
    # Collect all Python files first (or specified extensions)
    if file_extensions is None:
        file_extensions = [".py"]
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    all_files = []
    
    # Ensure paths is a list
    if isinstance(paths, str):
        paths = [paths]
        
    for path in paths:
        if os.path.isfile(path):
            if any(path.endswith(ext) for ext in file_extensions):
                all_files.append(path)
        else:
            for root, _, files in os.walk(path):
                for fn in files:
                    if any(fn.endswith(ext) for ext in file_extensions):
                        all_files.append(os.path.join(root, fn))
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Dynamic testing", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        try:
            res = run_python_file_with_random_inputs(path, runs=runs_per_file, timeout=timeout)
            results.append(res)
        except Exception as e:
            results.append({"path": path, "error": str(e)})
    return results

if __name__ == "__main__":
    import sys, json
    folder = sys.argv[1] if len(sys.argv) > 1 else "samples"
    out = scan_folder_dynamic(folder)
    print(json.dumps(out, indent=2))
