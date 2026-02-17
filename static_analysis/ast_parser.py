
"""
AST-based static feature extractor for Python (and best-effort Java).
Produces per-file and per-function feature dictionaries.
"""
import ast
import os

# optional Java parsing
try:
    import javalang
    _HAS_JAVALANG = True
except Exception:
    _HAS_JAVALANG = False

def extract_python_functions(source_code):
    """
    Returns list of (func_name, start_lineno, end_lineno, code_snippet, features)
    features: dict with simple structural metrics: num_statements, num_branches
    """
    tree = ast.parse(source_code)
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            # crudely determine end lineno by using body last node lineno
            end = getattr(node.body[-1], 'lineno', node.lineno) - 1
            # Extract source line snippet using ast.get_source_segment is best but not always available.
            snippet = ast.get_source_segment(source_code, node) or ""
            # structural features
            num_statements = sum(isinstance(n, ast.stmt) for n in ast.walk(node))
            num_branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(node))
            funcs.append({
                "name": node.name,
                "start": start,
                "end": end,
                "code": snippet,
                "features": {"num_statements": num_statements, "num_branches": num_branches}
            })
            
    # Fallback for script-style code (no functions)
    if not funcs and source_code.strip():
        # Check if there are any executable statements
        has_statements = any(isinstance(n, ast.stmt) for n in ast.walk(tree))
        if has_statements:
            num_statements = sum(isinstance(n, ast.stmt) for n in ast.walk(tree))
            num_branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(tree))
            funcs.append({
                "name": "<module_body>",
                "start": 0,
                "end": len(source_code.splitlines()),
                "code": source_code,
                "features": {"num_statements": num_statements, "num_branches": num_branches}
            })
            
    return funcs

def extract_python_file_features(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    funcs = extract_python_functions(source)
    file_features = {
        "path": filepath,
        "num_functions": len(funcs),
        "functions": funcs
    }
    return file_features

def extract_java_file_features(filepath):
    if not _HAS_JAVALANG:
        return {"path": filepath, "note": "javalang not available", "num_methods": 0, "methods": []}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    tree = javalang.parse.parse(source)
    methods = []
    for path, node in tree:
        # pick MethodDeclaration nodes
        if isinstance(node, javalang.tree.MethodDeclaration):
            name = node.name
            # javalang nodes may have position attribute
            snippet = ""  # skipping robust snippet extraction for brevity
            num_statements = len(node.body) if node.body else 0
            num_branches = sum(1 for n in node.body if hasattr(n, 'statements')) if node.body else 0
            methods.append({"name": name, "code": snippet, "features": {"num_statements": num_statements, "num_branches": num_branches}})
    return {"path": filepath, "num_methods": len(methods), "methods": methods}

def scan_code_folder(paths, show_progress=False, file_extensions=None):
    """
    Walk folders/files and extract features for files matching extensions.
    Returns list of file feature dicts.
    paths: list of file or directory paths
    file_extensions: list of extensions to include (e.g., ['.py', '.java']). If None, defaults to ['.py', '.java']
    """
    if file_extensions is None:
        file_extensions = ['.py', '.java', '.js', '.ts', '.cpp', '.c']
    # Normalize extensions to start with dot
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    
    results = []
    # Collect all files first for progress tracking
    all_files = []
    
    # Ensure paths is a list
    if isinstance(paths, str):
        paths = [paths]
        
    for path in paths:
        if os.path.isfile(path):
            # Handle single file case
            if any(path.endswith(ext) for ext in file_extensions):
                all_files.append(path)
        else:
            # Handle directory case
            for root, _, files in os.walk(path):
                for fn in files:
                    if any(fn.endswith(ext) for ext in file_extensions):
                        all_files.append(os.path.join(root, fn))
    
    # Use tqdm if available and show_progress is True
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(all_files, desc="Scanning files", unit="file")
        except ImportError:
            file_iter = all_files
    else:
        file_iter = all_files
    
    for path in file_iter:
        if path.endswith('.py'):
            try:
                results.append(extract_python_file_features(path))
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.java'):
            try:
                results.append(extract_java_file_features(path))
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.js') or path.endswith('.jsx') or path.endswith('.ts') or path.endswith('.tsx'):
            try:
                # Basic support for JS/TS
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    results.append({"path": path, "num_functions": 0, "functions": [], "note": "Basic JS/TS support"})
            except Exception as e:
                results.append({"path": path, "error": str(e)})
        elif path.endswith('.cpp') or path.endswith('.c') or path.endswith('.h'):
            try:
                # Basic support for C/C++
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    results.append({"path": path, "num_functions": 0, "functions": [], "note": "Basic C/C++ support"})
            except Exception as e:
                results.append({"path": path, "error": str(e)})
    return results

# quick demo function to run when module is executed directly
if __name__ == "__main__":
    import sys, json
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    feats = scan_code_folder(folder)
    print(json.dumps(feats, indent=2))
