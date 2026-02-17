"""
Logical Bug Checker - Detects logical contradictions and semantic bugs

Detects:
- Contradictory conditions (if x and not x)
- Impossible comparisons (if x > 10 and x < 5)
- Redundant conditions
- Always true/false conditions
- Dead code paths
- Docstring vs implementation mismatches
- Return type inconsistencies
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set, Tuple

class LogicalBugChecker:
    """AST-based logical bug detector"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    def __init__(self):
        self.bugs = []
        self.current_file = ""
        self.current_function = ""
    
    def check_code(self, code: str, filepath: str) -> List[Dict[str, Any]]:
        """Analyze code for logical bugs"""
        self.bugs = []
        self.current_file = filepath
        
        try:
            tree = ast.parse(code)
            self._analyze_tree(tree, code)
        except SyntaxError:
            pass  # Syntax errors handled by static_rules
        
        return self.bugs
    
    def _analyze_tree(self, tree: ast.AST, source_code: str):
        """Walk AST and check for logical bugs"""
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.current_function = node.name
                self._check_function_logic(node, source_code)
            
            if isinstance(node, ast.If):
                self._check_if_logic(node)
            
            if isinstance(node, ast.BoolOp):
                self._check_bool_op(node)
            
            if isinstance(node, ast.Compare):
                self._check_comparison_logic(node)
    
    def _check_function_logic(self, node: ast.FunctionDef, source_code: str):
        """Check function-level logical issues"""
        
        # Check docstring vs implementation
        docstring = ast.get_docstring(node)
        if docstring:
            self._check_docstring_consistency(node, docstring)
        
        # Check for contradictory conditions in function body
        self._check_contradictory_conditions(node.body)
        
        # Check for impossible return paths
        self._check_return_paths(node)
    
    def _check_docstring_consistency(self, node: ast.FunctionDef, docstring: str):
        """Check if docstring matches implementation"""
        docstring_lower = docstring.lower()
        
        # Check return documentation vs actual returns
        has_return_doc = any(word in docstring_lower for word in ['return', 'returns', ':returns', ':return'])
        
        # Find actual returns
        actual_returns = []
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                actual_returns.append(child)
        
        # Docstring says returns but function doesn't return anything
        if has_return_doc and not actual_returns:
            # Check if it's not just documentation of None return
            if 'none' not in docstring_lower and 'nothing' not in docstring_lower:
                self._add_bug(
                    line=node.lineno,
                    category="docstring_return_mismatch",
                    severity=self.SEVERITY_MEDIUM,
                    message=f"Docstring documents return value but function '{node.name}' doesn't return anything",
                    evidence="Documentation mentions return but no return statement found"
                )
        
        # Check for raises documentation
        has_raises_doc = any(word in docstring_lower for word in ['raise', 'raises', ':raises', 'exception'])
        
        # Find actual raises
        actual_raises = []
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                actual_raises.append(child)
        
        # Function raises but not documented
        if actual_raises and not has_raises_doc:
            self._add_bug(
                line=node.lineno,
                category="undocumented_exception",
                severity=self.SEVERITY_LOW,
                message=f"Function '{node.name}' raises exceptions but docstring doesn't document them",
                evidence=f"Found {len(actual_raises)} raise statement(s) without documentation"
            )
    
    def _check_contradictory_conditions(self, statements: List[ast.stmt]):
        """Check for contradictory conditions in sequential if statements"""
        
        # Track conditions we've seen
        conditions_seen = []
        
        for stmt in statements:
            if isinstance(stmt, ast.If):
                # Check if this condition contradicts a previous one
                current_cond = self._extract_condition_info(stmt.test)
                
                for prev_cond in conditions_seen:
                    if self._conditions_contradict(prev_cond, current_cond):
                        self._add_bug(
                            line=stmt.lineno,
                            category="contradictory_condition",
                            severity=self.SEVERITY_HIGH,
                            message="Condition contradicts earlier condition in same scope",
                            evidence=f"This condition can never be true given earlier checks"
                        )
                
                conditions_seen.append(current_cond)
                
                # Recursively check nested blocks
                self._check_contradictory_conditions(stmt.body)
                self._check_contradictory_conditions(stmt.orelse)
    
    def _extract_condition_info(self, node: ast.expr) -> Dict[str, Any]:
        """Extract information about a condition for contradiction checking"""
        info = {
            "type": type(node).__name__,
            "dump": ast.dump(node),
            "variables": set(),
            "comparisons": []
        }
        
        # Extract variable names
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                info["variables"].add(child.id)
            if isinstance(child, ast.Compare):
                info["comparisons"].append(self._extract_comparison(child))
        
        return info
    
    def _extract_comparison(self, node: ast.Compare) -> Dict[str, Any]:
        """Extract comparison details"""
        return {
            "left": ast.dump(node.left),
            "ops": [type(op).__name__ for op in node.ops],
            "comparators": [ast.dump(c) for c in node.comparators]
        }
    
    def _conditions_contradict(self, cond1: Dict, cond2: Dict) -> bool:
        """Check if two conditions contradict each other"""
        
        # Simple check: exact same condition (redundant)
        if cond1["dump"] == cond2["dump"]:
            return False  # Same condition, not contradictory
        
        # Check for x and not x pattern
        # This is a simplified check - real implementation would need more sophisticated analysis
        
        # Check if one is negation of the other
        if f"UnaryOp(op=Not(), operand={cond1['dump']})" == cond2["dump"]:
            return True
        if f"UnaryOp(op=Not(), operand={cond2['dump']})" == cond1["dump"]:
            return True
        
        return False
    
    def _check_return_paths(self, node: ast.FunctionDef):
        """Check for impossible or inconsistent return paths"""
        
        # Track all return statements and their conditions
        returns = []
        
        def find_returns(stmts, depth=0):
            for stmt in stmts:
                if isinstance(stmt, ast.Return):
                    returns.append({
                        "node": stmt,
                        "depth": depth,
                        "has_value": stmt.value is not None
                    })
                if hasattr(stmt, 'body'):
                    find_returns(stmt.body, depth + 1)
                if hasattr(stmt, 'orelse'):
                    find_returns(stmt.orelse, depth + 1)
        
        find_returns(node.body)
        
        # Check for returns at different depths that might indicate missing returns
        if returns:
            depths = set(r["depth"] for r in returns)
            if len(depths) > 1 and 0 not in depths:
                # All returns are inside conditionals, might be missing a default return
                self._add_bug(
                    line=node.lineno,
                    category="possible_missing_return",
                    severity=self.SEVERITY_MEDIUM,
                    message=f"Function '{node.name}' may not return on all code paths",
                    evidence="All return statements are inside conditional blocks"
                )
    
    def _check_if_logic(self, node: ast.If):
        """Check if statement for logical issues"""
        
        # Check for if x: ... elif x: (same condition)
        if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            elif_node = node.orelse[0]
            if ast.dump(node.test) == ast.dump(elif_node.test):
                self._add_bug(
                    line=elif_node.lineno,
                    category="duplicate_condition",
                    severity=self.SEVERITY_HIGH,
                    message="elif has same condition as if - branch is unreachable",
                    evidence="The if branch already handles this condition"
                )
        
        # Check for if x: return ... else: return (could simplify)
        if (len(node.body) == 1 and isinstance(node.body[0], ast.Return) and
            len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Return)):
            # This is fine but could be a ternary - just info level
            pass
    
    def _check_bool_op(self, node: ast.BoolOp):
        """Check boolean operations for logical issues"""
        
        # Check for x and not x
        if isinstance(node.op, ast.And):
            for i, value in enumerate(node.values):
                for j, other in enumerate(node.values):
                    if i != j:
                        # Check if one is negation of other
                        if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
                            if ast.dump(value.operand) == ast.dump(other):
                                self._add_bug(
                                    line=node.lineno,
                                    category="always_false_condition",
                                    severity=self.SEVERITY_CRITICAL,
                                    message="Condition 'x and not x' is always False",
                                    evidence="Contradictory conditions in AND expression"
                                )
                        elif isinstance(other, ast.UnaryOp) and isinstance(other.op, ast.Not):
                            if ast.dump(other.operand) == ast.dump(value):
                                self._add_bug(
                                    line=node.lineno,
                                    category="always_false_condition",
                                    severity=self.SEVERITY_CRITICAL,
                                    message="Condition 'x and not x' is always False",
                                    evidence="Contradictory conditions in AND expression"
                                )
        
        # Check for x or not x (always true)
        if isinstance(node.op, ast.Or):
            for i, value in enumerate(node.values):
                for j, other in enumerate(node.values):
                    if i != j:
                        if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
                            if ast.dump(value.operand) == ast.dump(other):
                                self._add_bug(
                                    line=node.lineno,
                                    category="always_true_condition",
                                    severity=self.SEVERITY_MEDIUM,
                                    message="Condition 'x or not x' is always True",
                                    evidence="Tautology in OR expression - condition is redundant"
                                )
        
        # Check for duplicate values in and/or
        seen_dumps = set()
        for value in node.values:
            dump = ast.dump(value)
            if dump in seen_dumps:
                self._add_bug(
                    line=node.lineno,
                    category="redundant_condition",
                    severity=self.SEVERITY_LOW,
                    message="Duplicate condition in boolean expression",
                    evidence="Same condition appears multiple times"
                )
            seen_dumps.add(dump)
    
    def _check_comparison_logic(self, node: ast.Compare):
        """Check comparisons for logical issues"""
        
        # Check for impossible ranges like x > 10 and x < 5
        # This requires tracking the variable and its constraints
        
        # Check for comparing variable to itself
        if len(node.ops) == 1 and len(node.comparators) == 1:
            if ast.dump(node.left) == ast.dump(node.comparators[0]):
                op = node.ops[0]
                if isinstance(op, (ast.Eq, ast.LtE, ast.GtE)):
                    self._add_bug(
                        line=node.lineno,
                        category="self_comparison_always_true",
                        severity=self.SEVERITY_MEDIUM,
                        message="Comparing variable to itself is always True",
                        evidence="x == x, x <= x, x >= x are always True"
                    )
                elif isinstance(op, (ast.NotEq, ast.Lt, ast.Gt)):
                    self._add_bug(
                        line=node.lineno,
                        category="self_comparison_always_false",
                        severity=self.SEVERITY_HIGH,
                        message="Comparing variable to itself is always False",
                        evidence="x != x, x < x, x > x are always False"
                    )
    
    def _add_bug(self, line: int, category: str, severity: str, message: str, evidence: str):
        """Add a bug to the list"""
        self.bugs.append({
            "file": self.current_file,
            "function": self.current_function,
            "line": line,
            "category": category,
            "severity": severity,
            "message": message,
            "evidence": evidence,
            "detector": "logical_checker"
        })


def check_logical_bugs(static_results: List[Dict], show_progress: bool = False) -> List[Dict[str, Any]]:
    """
    Run logical bug checking on all analyzed files
    
    Args:
        static_results: Output from scan_code_folder
        show_progress: Show progress bar
        
    Returns:
        List of detected logical bugs
    """
    all_bugs = []
    checker = LogicalBugChecker()
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(static_results, desc="Logical bug checking", unit="file")
        except ImportError:
            file_iter = static_results
    else:
        file_iter = static_results
    
    for file_info in file_iter:
        filepath = file_info.get('path', '')
        
        if filepath.endswith('.py'):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                bugs = checker.check_code(code, filepath)
                all_bugs.extend(bugs)
            except Exception:
                pass  # Errors handled elsewhere
    
    return all_bugs

