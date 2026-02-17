import ast
import sys
import os

# Global set to store executed line numbers
executed_lines = set()

def trace_calls(frame, event, arg):
    if event == 'line':
        executed_lines.add(frame.f_lineno)
    return trace_calls

def generate_mermaid_ast(node, executed_lines):
    """
    Generates a Mermaid graph definition for the AST.
    Highlights nodes that correspond to executed lines.
    """
    lines = ["graph TD"]
    
    def walk(node, parent_id=None):
        node_id = str(id(node))
        node_type = type(node).__name__
        
        # Label for the node
        label = node_type
        if hasattr(node, 'name'):
            label += f"\\n({node.name})"
        elif hasattr(node, 'id'):
            label += f"\\n({node.id})"
        elif isinstance(node, ast.Constant):
            label += f"\\n({node.value})"
            
        lines.append(f'    {node_id}["{label}"]')
        
        # Edge from parent
        if parent_id:
            lines.append(f"    {parent_id} --> {node_id}")
            
        # Highlight if executed
        if hasattr(node, 'lineno') and node.lineno in executed_lines:
            lines.append(f"    style {node_id} fill:#9f9,stroke:#333,stroke-width:2px")
        
        # Recurse
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        walk(item, node_id)
            elif isinstance(value, ast.AST):
                walk(value, node_id)

    walk(node)
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_trace.py <file_to_trace>")
        return

    target_file = sys.argv[1]
    
    if not os.path.exists(target_file):
        print(f"Error: File {target_file} not found")
        return

    # 1. Parse AST
    with open(target_file, "r") as f:
        source = f.read()
    tree = ast.parse(source)

    # 2. Run code with tracer
    print(f"[*] Running {target_file} with trace...")
    sys.settrace(trace_calls)
    try:
        # We execute the code in a separate namespace to avoid polluting ours
        exec(source, {})
    except Exception as e:
        print(f"Execution error (expected for buggy files): {e}")
    finally:
        sys.settrace(None)

    print(f"[*] Executed lines: {sorted(list(executed_lines))}")

    # 3. Generate Diagram
    print("[*] Generating Mermaid diagram...")
    mermaid_code = generate_mermaid_ast(tree, executed_lines)
    
    output_file = target_file + ".mmd"
    with open(output_file, "w") as f:
        f.write(mermaid_code)
    
    print(f"[*] Diagram saved to {output_file}")
    print("    (You can view this file in a Mermaid Live Editor or VS Code extension)")

if __name__ == "__main__":
    main()
