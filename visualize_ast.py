import ast
import argparse
import os

def print_ast(node, level=0):
    indent = "  " * level
    if isinstance(node, ast.AST):
        print(f"{indent}{type(node).__name__}")
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        print_ast(item, level + 1)
            elif isinstance(value, ast.AST):
                print_ast(value, level + 1)

def main():
    parser = argparse.ArgumentParser(description="Visualize AST in Terminal")
    parser.add_argument("file", help="Python file to parse")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        return

    with open(args.file, "r") as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
        print(f"AST for {args.file}:")
        print("=" * 40)
        # Option 1: Built-in dump (detailed but hard to read)
        # print(ast.dump(tree, indent=2))
        
        # Option 2: Custom simplified tree print
        print_ast(tree)
        print("=" * 40)
    except Exception as e:
        print(f"Failed to parse: {e}")

if __name__ == "__main__":
    main()
