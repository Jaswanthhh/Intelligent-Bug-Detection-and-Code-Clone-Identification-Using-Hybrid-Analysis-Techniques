import ast
import sys
import os

# Global set to store executed line numbers for the current trace
_executed_lines = set()

def _trace_calls(frame, event, arg):
    if event == 'line':
        _executed_lines.add(frame.f_lineno)
    return _trace_calls

def _generate_mermaid_ast(node, executed_lines):
    """
    Generates a simplified Mermaid graph definition for the AST.
    Highlights nodes that correspond to executed lines.
    """
    lines = ["graph TD"]
    
    # Nodes to skip to simplify the graph
    SKIP_TYPES = {
        'Load', 'Store', 'Del', 'arguments', 'arg', 'alias', 'keyword',
        'Expr', 'Attribute', 'Name', 'Constant', 'Str', 'Num', 'NameConstant'
    }
    
    # Nodes to explicitly include (Control flow & Structure)
    INCLUDE_TYPES = {
        'Module', 'ClassDef', 'FunctionDef', 'AsyncFunctionDef',
        'If', 'For', 'AsyncFor', 'While', 'Try', 'ExceptHandler',
        'Return', 'Raise', 'Break', 'Continue', 'Call', 'Assign', 'AugAssign'
    }

    def walk(node, parent_id=None):
        node_type = type(node).__name__
        
        # Simplification Logic
        should_show = node_type in INCLUDE_TYPES
        
        # If it's a Call, we definitely want to show it
        # If it's a structural node, show it
        
        if not should_show:
            # If we skip this node, we still might want to process its children
            # but we need to connect parent to children directly?
            # Or just stop recursion? 
            # Better approach: Only traverse and draw "Interesting" nodes.
            # But we need to maintain the tree structure.
            
            # Alternative: Just recurse but don't draw THIS node?
            # If we don't draw this node, we pass parent_id to children.
            pass
        
        node_id = str(id(node))
        
        if should_show:
            # Label for the node
            label = node_type
            if hasattr(node, 'name'):
                label += f"\\n{node.name}"
            elif hasattr(node, 'id'):
                label += f"\\n{node.id}"
            elif isinstance(node, ast.Call):
                # Try to get function name
                if isinstance(node.func, ast.Name):
                    label += f"\\n{node.func.id}()"
                elif isinstance(node.func, ast.Attribute):
                    label += f"\\n.{node.func.attr}()"
                else:
                    label += "\\nCall"

            lines.append(f'    {node_id}["{label}"]')
            
            # Edge from parent
            if parent_id:
                lines.append(f"    {parent_id} --> {node_id}")
                
            # Highlight if executed
            if hasattr(node, 'lineno') and node.lineno in executed_lines:
                lines.append(f"    style {node_id} fill:#9f9,stroke:#333,stroke-width:2px")
            
            # Update parent_id for children
            current_parent_id = node_id
        else:
            # If we don't show this node, children connect to *our* parent
            current_parent_id = parent_id

        # Recurse
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        walk(item, current_parent_id)
            elif isinstance(value, ast.AST):
                walk(value, current_parent_id)

    walk(node)
    return "\n".join(lines)

def generate_ast_diagram(target_file):
    """
    Runs the target file, captures execution trace, and generates a .mmd file.
    Returns the path to the generated diagram or None on failure.
    """
    global _executed_lines
    if not os.path.exists(target_file):
        return None

    # Clear previous trace
    _executed_lines.clear()

    # 1. Parse AST
    try:
        with open(target_file, "r") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception as e:
        print(f"Failed to parse {target_file}: {e}")
        return None

    # 2. Run code with tracer
    # We use a separate global variable for the tracer to access
    
    sys.settrace(_trace_calls)
    try:
        # Execute in a restricted namespace to avoid side effects
        exec(source, {'__name__': '__main__'})
    except Exception:
        # Ignore runtime errors during tracing (we just want coverage)
        pass
    finally:
        sys.settrace(None)

    # 3. Generate Diagram
    mermaid_code = _generate_mermaid_ast(tree, _executed_lines)
    
    output_file = target_file + ".mmd"
    with open(output_file, "w") as f:
        f.write(mermaid_code)
        
    return output_file

# Java Support
try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False

def _generate_mermaid_java_ast(node, executed_methods):
    """
    Generates a simplified Mermaid graph for Java AST.
    Highlights MethodDeclaration nodes if they are in executed_methods.
    """
    lines = ["graph TD"]
    
    # Java nodes to include
    INCLUDE_TYPES = {
        'ClassDeclaration', 'MethodDeclaration', 'ConstructorDeclaration',
        'IfStatement', 'WhileStatement', 'ForStatement', 'DoStatement',
        'TryStatement', 'CatchClause', 'ThrowStatement', 'ReturnStatement',
        'MethodInvocation', 'ClassCreator', 'Assignment'
    }
    
    def walk(node, parent_id=None):
        node_id = str(id(node))
        node_type = type(node).__name__
        
        should_show = node_type in INCLUDE_TYPES
        
        if should_show:
            label = node_type
            if hasattr(node, 'name'):
                label += f"\\n{node.name}"
            elif node_type == 'MethodInvocation':
                if hasattr(node, 'member'):
                    label += f"\\n.{node.member}()"
            
            lines.append(f'    {node_id}["{label}"]')
            
            if parent_id:
                lines.append(f"    {parent_id} --> {node_id}")
                
            # Highlight executed methods
            if node_type == 'MethodDeclaration' and node.name in executed_methods:
                 lines.append(f"    style {node_id} fill:#9f9,stroke:#333,stroke-width:2px")
            
            current_parent_id = node_id
        else:
            current_parent_id = parent_id
        
        # Recurse
        if hasattr(node, 'children'):
            if isinstance(node, (javalang.ast.Node, list, tuple)):
                children = node if isinstance(node, (list, tuple)) else node.children
                if children:
                    for child in children:
                        if isinstance(child, (list, tuple)):
                            for item in child:
                                if isinstance(item, javalang.ast.Node):
                                    walk(item, current_parent_id)
                        elif isinstance(child, javalang.ast.Node):
                            walk(child, current_parent_id)

    walk(node)
    return "\n".join(lines)

def generate_java_ast_diagram(target_file, bci_jar_path="bci_injector.jar"):
    if not JAVALANG_AVAILABLE:
        print("javalang not installed, skipping Java visualization")
        return None
        
    if not os.path.exists(target_file):
        return None

    # 1. Parse
    try:
        with open(target_file, 'r') as f:
            source = f.read()
        tree = javalang.parse.parse(source)
    except Exception as e:
        print(f"Failed to parse Java file {target_file}: {e}")
        return None

    # 2. Run BCI to get trace
    # We need to import the collector here to avoid circular imports if possible, 
    # or just use subprocess if we want to be safe, but importing is better.
    from bci_tracing.java_trace_collector import JavaTraceCollector
    
    collector = JavaTraceCollector(bci_jar_path)
    result = collector.run_java_with_bci(target_file)
    
    executed_methods = set()
    if result['success'] and result['trace_file']:
        analysis = collector.analyze_trace_file(result['trace_file'])
        # analysis['method_counts'] keys are method names
        executed_methods = set(analysis.get('method_counts', {}).keys())
    
    # 3. Generate Diagram
    mermaid_code = _generate_mermaid_java_ast(tree, executed_methods)
    
    output_file = target_file + ".mmd"
    with open(output_file, "w") as f:
        f.write(mermaid_code)
        
    return output_file
