import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from visualization.ast_visualizer import generate_ast_diagram

target = "samples/sample_safe_1.py"
print(f"Testing visualization on {target}...")

try:
    out = generate_ast_diagram(target)
    print(f"Generated: {out}")
    
    if out and os.path.exists(out):
        with open(out, "r") as f:
            content = f.read()
            print("\n--- Content Snippet ---")
            print(content[:500])
            print("-----------------------")
            
            if "Load" in content:
                print("FAIL: 'Load' node found (Simplification NOT working)")
            else:
                print("SUCCESS: 'Load' node NOT found (Simplification working)")
    else:
        print("Failed to generate file.")

except Exception as e:
    print(f"Error: {e}")
