# sample_safe_2.py
def sum_two(x, y):
    return x + y

def maybe_throw(s):
    # very rarely throws intentionally if RANDOM_INPUT contains 'Z'
    import os
    if 'Z' in os.environ.get("RANDOM_INPUT",""):
        raise ValueError("Intentional rare error")
    return True

if __name__ == "__main__":
    import os
    print("sample_safe_2 running", os.environ.get("RANDOM_INPUT","")[:6])
