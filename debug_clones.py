import os
import sys

# Ensure we can import from current directory
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")

# Import the module under test
try:
    from semantic_analysis import llm_embeddings
    print("Successfully imported llm_embeddings")
    print(f"SENTENCE_TRANSFORMERS_AVAILABLE: {llm_embeddings.SENTENCE_TRANSFORMERS_AVAILABLE}")
    print(f"SKLEARN_AVAILABLE: {llm_embeddings.SKLEARN_AVAILABLE}")
except ImportError as e:
    print(f"Failed to import llm_embeddings: {e}")
    sys.exit(1)

# Define test snippets
snippets = [
    {"file": "a.py", "func_name": "foo", "code": "def foo(x): return x + 1"},
    {"file": "b.py", "func_name": "bar", "code": "def bar(y): return y + 1"}, # Type-2 clone
    {"file": "c.py", "func_name": "baz", "code": "def baz(z): return z * 2"},
    {"file": "exact.py", "func_name": "foo_copy", "code": "def foo(x): return x + 1"} # Type-1 clone
]

print("\n--- Testing Synthetic Data ---")
pairs = llm_embeddings.find_similar_pairs(snippets, threshold=0.1, show_progress=False)
print(f"Found {len(pairs)} pairs (threshold=0.1)")
for p in pairs:
    print(f"  {p['a']['file']} <-> {p['b']['file']}: {p['score']:.4f}")

# Test with actual samples
print("\n--- Testing Actual Samples ---")
sample_dir = "samples"
if os.path.exists(sample_dir):
    real_snippets = []
    # Read a few key files
    target_files = ["sample_safe_1.py", "exact_clone.py", "math_utils.py", "math_utils_clone.py"]
    for fname in target_files:
        path = os.path.join(sample_dir, fname)
        if os.path.exists(path):
            with open(path, "r") as f:
                code = f.read()
                real_snippets.append({"file": fname, "func_name": "main", "code": code})
        else:
            print(f"Missing file: {path}")
            
    if len(real_snippets) > 1:
        pairs = llm_embeddings.find_similar_pairs(real_snippets, threshold=0.1)
        print(f"Found {len(pairs)} pairs in samples (threshold=0.1)")
        for p in pairs:
            print(f"  {p['a']['file']} <-> {p['b']['file']}: {p['score']:.4f}")
    else:
        print("Not enough sample files found.")
else:
    print("Samples directory not found.")
