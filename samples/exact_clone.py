# sample_safe_1.py
def add(a, b):
    """Simple add"""
    return a + b

if __name__ == "__main__":
    # uses env var RANDOM_INPUT for demo
    import os
    x = os.environ.get("RANDOM_INPUT", "0")
    # print a small message and exit normally
    print("sample_safe_1 running with", x[:8])
