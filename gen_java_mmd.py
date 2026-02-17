import os
import sys

# Add current directory to path so we can import visualization
sys.path.append(os.getcwd())

try:
    from visualization.ast_visualizer import generate_java_ast_diagram
    
    files = [
        "samples/SampleJava1.java",
        "samples/SampleJava2.java",
        "samples/SampleBuggy.java"
    ]
    
    print("Generating Java AST diagrams...")
    for f in files:
        if os.path.exists(f):
            print(f"Processing {f}...")
            out = generate_java_ast_diagram(f, "bci_injector.jar")
            print(f"Result: {out}")
        else:
            print(f"File not found: {f}")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
