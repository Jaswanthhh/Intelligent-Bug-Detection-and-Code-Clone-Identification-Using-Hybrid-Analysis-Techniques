"""
Static Bug Detection Rules - AST-based analysis for Python and Java

Detects:
- Unused variables/parameters
- Suspicious comparisons (== None vs is None)
- Empty exception handlers
- Bare except clauses
- Unreachable code after return/raise
- Division by zero risks
- Type confusion patterns
- Mutable default arguments
- Shadowed built-ins
"""

import ast
import re
from typing import List, Dict, Any, Optional

class StaticBugDetector:
    """AST-based static bug detector for Python code"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    SEVERITY_INFO = "info"
    
    # Python built-ins that shouldn't be shadowed
    PYTHON_BUILTINS = {
        'list', 'dict', 'set', 'str', 'int', 'float', 'bool', 'tuple',
        'type', 'id', 'len', 'range', 'print', 'input', 'open', 'file',
        'map', 'filter', 'sum', 'min', 'max', 'abs', 'round', 'sorted',
        'reversed', 'enumerate', 'zip', 'any', 'all', 'iter', 'next',
        'object', 'super', 'property', 'staticmethod', 'classmethod',
        'format', 'repr', 'hash', 'callable', 'isinstance', 'issubclass',
        'getattr', 'setattr', 'hasattr', 'delattr', 'vars', 'dir',
        'globals', 'locals', 'eval', 'exec', 'compile', 'help'
    }
    
    def __init__(self):
        self.bugs = []
        self.current_file = ""
        self.current_function = ""
    
    def detect_bugs_in_code(self, code: str, filepath: str) -> List[Dict[str, Any]]:
        """Analyze Python code and return list of detected bugs"""
        self.bugs = []
        self.current_file = filepath
        
        try:
            tree = ast.parse(code)
            self._analyze_tree(tree, code)
        except SyntaxError as e:
            self.bugs.append({
                "file": filepath,
                "function": None,
                "line": e.lineno or 0,
                "category": "syntax_error",
                "severity": self.SEVERITY_CRITICAL,
                "message": f"Syntax error: {e.msg}",
                "evidence": str(e),
                "detector": "static_rules"
            })
        
        return self.bugs
    
    def _analyze_tree(self, tree: ast.AST, source_code: str):
        """Walk AST and apply all detection rules"""
        
        for node in ast.walk(tree):
            # Analyze functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.current_function = node.name
                self._check_function(node, source_code)
            
            # Analyze exception handlers
            if isinstance(node, ast.ExceptHandler):
                self._check_exception_handler(node)
            
            # Analyze comparisons
            if isinstance(node, ast.Compare):
                self._check_comparison(node)
            
            # Analyze assignments
            if isinstance(node, ast.Assign):
                self._check_assignment(node)
            
            # Analyze if statements
            if isinstance(node, ast.If):
                self._check_if_statement(node)
            
            # Analyze binary operations (division)
            if isinstance(node, ast.BinOp):
                self._check_binary_op(node)
            
            # Analyze try blocks
            if isinstance(node, ast.Try):
                self._check_try_block(node)

            # Analyze function calls for Security Taints
            if isinstance(node, ast.Call):
                self._check_call(node)
    
    def _check_function(self, node: ast.FunctionDef, source_code: str):
        """Check function-level bugs"""
        
        # Check for mutable default arguments
        for default in node.args.defaults + node.args.kw_defaults:
            if default is not None and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add_bug(
                    line=node.lineno,
                    category="mutable_default_argument",
                    severity=self.SEVERITY_HIGH,
                    message=f"Mutable default argument in function '{node.name}'. Use None and initialize inside function.",
                    evidence=f"def {node.name}(..., arg={ast.dump(default)})"
                )
        
        # Check for unused parameters
        param_names = set()
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            param_names.add(arg.arg)
        if node.args.vararg:
            param_names.add(node.args.vararg.arg)
        if node.args.kwarg:
            param_names.add(node.args.kwarg.arg)
        
        # Remove 'self' and 'cls' from check
        param_names -= {'self', 'cls'}
        
        # Find used names in function body
        used_names = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                used_names.add(child.id)
        
        unused_params = param_names - used_names
        for param in unused_params:
            self._add_bug(
                line=node.lineno,
                category="unused_parameter",
                severity=self.SEVERITY_LOW,
                message=f"Unused parameter '{param}' in function '{node.name}'",
                evidence=f"Parameter '{param}' is never used in function body"
            )
        
        # Check for shadowed built-ins in parameters
        shadowed = param_names & self.PYTHON_BUILTINS
        for name in shadowed:
            self._add_bug(
                line=node.lineno,
                category="shadowed_builtin",
                severity=self.SEVERITY_MEDIUM,
                message=f"Parameter '{name}' shadows built-in in function '{node.name}'",
                evidence=f"Built-in '{name}' is shadowed by function parameter"
            )
        
        # Check for unreachable code after return/raise
        self._check_unreachable_code(node.body)
        
        # Check for missing return in non-void function
        self._check_missing_return(node)
    
    def _check_unreachable_code(self, statements: List[ast.stmt]):
        """Check for code after return/raise/break/continue"""
        for i, stmt in enumerate(statements):
            if isinstance(stmt, (ast.Return, ast.Raise)) and i < len(statements) - 1:
                next_stmt = statements[i + 1]
                self._add_bug(
                    line=next_stmt.lineno,
                    category="unreachable_code",
                    severity=self.SEVERITY_HIGH,
                    message="Unreachable code after return/raise statement",
                    evidence=f"Code at line {next_stmt.lineno} will never execute"
                )
            
            # Recursively check nested blocks
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With)):
                if hasattr(stmt, 'body'):
                    self._check_unreachable_code(stmt.body)
                if hasattr(stmt, 'orelse'):
                    self._check_unreachable_code(stmt.orelse)
    
    def _check_missing_return(self, node: ast.FunctionDef):
        """Check if function has inconsistent return patterns"""
        returns = []
        
        def find_returns(stmts):
            for stmt in stmts:
                if isinstance(stmt, ast.Return):
                    returns.append(stmt)
                elif hasattr(stmt, 'body'):
                    find_returns(stmt.body)
                if hasattr(stmt, 'orelse'):
                    find_returns(stmt.orelse)
        
        find_returns(node.body)
        
        # Check for mixed return patterns (some return value, some don't)
        returns_value = [r for r in returns if r.value is not None]
        returns_none = [r for r in returns if r.value is None]
        
        if returns_value and returns_none:
            self._add_bug(
                line=node.lineno,
                category="inconsistent_return",
                severity=self.SEVERITY_MEDIUM,
                message=f"Function '{node.name}' has inconsistent return statements",
                evidence=f"Some paths return a value, others return None implicitly"
            )
    
    def _check_exception_handler(self, node: ast.ExceptHandler):
        """Check exception handler patterns"""
        
        # Bare except clause
        if node.type is None:
            self._add_bug(
                line=node.lineno,
                category="bare_except",
                severity=self.SEVERITY_HIGH,
                message="Bare 'except:' clause catches all exceptions including KeyboardInterrupt and SystemExit",
                evidence="Use 'except Exception:' or specific exception types",
                suggestion="except Exception as e:\n    # Log the error\n    import logging\n    logging.error(e)"
            )
        
        # Empty exception handler
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self._add_bug(
                line=node.lineno,
                category="empty_exception_handler",
                severity=self.SEVERITY_HIGH,
                message="Empty exception handler silently swallows errors",
                evidence="Exception is caught but not handled or logged",
                suggestion="# Add logging or comment\n    import logging\n    logging.warn('Exception ignored')"
            )
        
        # Catching too broad exception
        if node.type and isinstance(node.type, ast.Name):
            if node.type.id == 'Exception':
                # Check if it's just pass or just logging
                if len(node.body) == 1:
                    if isinstance(node.body[0], ast.Pass):
                        self._add_bug(
                            line=node.lineno,
                            category="swallowed_exception",
                            severity=self.SEVERITY_CRITICAL,
                            message="Catching broad 'Exception' and ignoring it",
                            evidence="This hides all errors and makes debugging impossible"
                        )
    
    def _check_comparison(self, node: ast.Compare):
        """Check suspicious comparison patterns"""
        
        for i, (op, comparator) in enumerate(zip(node.ops, node.comparators)):
            left = node.left if i == 0 else node.comparators[i - 1]
            
            # Check == None instead of is None
            if isinstance(op, ast.Eq):
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    self._add_bug(
                        line=node.lineno,
                        category="equality_none_comparison",
                        severity=self.SEVERITY_MEDIUM,
                        message="Use 'is None' instead of '== None'",
                        evidence="'== None' can be overridden by __eq__, use 'is None' for identity check",
                        suggestion="is None"
                    )
                elif isinstance(left, ast.Constant) and left.value is None:
                    self._add_bug(
                        line=node.lineno,
                        category="equality_none_comparison",
                        severity=self.SEVERITY_MEDIUM,
                        message="Use 'is None' instead of '== None'",
                        evidence="'== None' can be overridden by __eq__, use 'is None' for identity check"
                    )
            
            # Check != None instead of is not None
            if isinstance(op, ast.NotEq):
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    self._add_bug(
                        line=node.lineno,
                        category="inequality_none_comparison",
                        severity=self.SEVERITY_MEDIUM,
                        message="Use 'is not None' instead of '!= None'",
                        evidence="'!= None' can be overridden by __eq__, use 'is not None' for identity check"
                    )
            
            # Check comparing different types (string to int, etc.)
            if isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                if isinstance(left, ast.Constant) and isinstance(comparator, ast.Constant):
                    if type(left.value) != type(comparator.value) and left.value is not None and comparator.value is not None:
                        self._add_bug(
                            line=node.lineno,
                            category="type_mismatch_comparison",
                            severity=self.SEVERITY_HIGH,
                            message=f"Comparing different types: {type(left.value).__name__} and {type(comparator.value).__name__}",
                            evidence="This comparison may always be False or raise TypeError"
                        )
    
    def _check_assignment(self, node: ast.Assign):
        """Check assignment patterns"""
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check shadowing built-ins
                if target.id in self.PYTHON_BUILTINS:
                    self._add_bug(
                        line=node.lineno,
                        category="shadowed_builtin",
                        severity=self.SEVERITY_MEDIUM,
                        message=f"Assignment shadows built-in '{target.id}'",
                        evidence=f"Variable '{target.id}' shadows Python built-in"
                    )
    
    def _check_if_statement(self, node: ast.If):
        """Check if statement patterns"""
        
        # Check for constant condition
        if isinstance(node.test, ast.Constant):
            if node.test.value is True:
                self._add_bug(
                    line=node.lineno,
                    category="constant_condition",
                    severity=self.SEVERITY_MEDIUM,
                    message="Condition is always True",
                    evidence="'if True:' makes the else branch unreachable"
                )
            elif node.test.value is False:
                self._add_bug(
                    line=node.lineno,
                    category="constant_condition",
                    severity=self.SEVERITY_HIGH,
                    message="Condition is always False",
                    evidence="'if False:' makes the if branch unreachable (dead code)"
                )
        
        # Check for duplicate conditions in elif chain
        self._check_duplicate_conditions(node)
    
    def _check_duplicate_conditions(self, node: ast.If):
        """Check for duplicate conditions in if/elif chain"""
        conditions = [ast.dump(node.test)]
        
        current = node
        while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
            cond_dump = ast.dump(current.test)
            if cond_dump in conditions:
                self._add_bug(
                    line=current.lineno,
                    category="duplicate_condition",
                    severity=self.SEVERITY_HIGH,
                    message="Duplicate condition in if/elif chain",
                    evidence="This condition was already checked earlier, branch is unreachable"
                )
            conditions.append(cond_dump)
    
    def _check_binary_op(self, node: ast.BinOp):
        """Check binary operations for potential issues"""
        
        # Check division by zero
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                self._add_bug(
                    line=node.lineno,
                    category="division_by_zero",
                    severity=self.SEVERITY_CRITICAL,
                    message="Division by zero",
                    evidence="This will raise ZeroDivisionError at runtime"
                )
    
    def _check_try_block(self, node: ast.Try):
        """Check try block patterns"""
        
        # Check for try without except or finally
        if not node.handlers and not node.finalbody:
            self._add_bug(
                line=node.lineno,
                category="useless_try",
                severity=self.SEVERITY_LOW,
                message="Try block without except or finally",
                evidence="This try block has no effect"
            )
        
        # Check for except after bare except
        bare_except_found = False
        for handler in node.handlers:
            if handler.type is None:
                bare_except_found = True
            elif bare_except_found:
                self._add_bug(
                    line=handler.lineno,
                    category="unreachable_except",
                    severity=self.SEVERITY_HIGH,
                    message="Exception handler after bare except is unreachable",
                    evidence="Bare 'except:' catches everything, subsequent handlers never execute"
                )

    def _check_call(self, node: ast.Call):
        """Check function calls for Security Vulnerability (Taint) patterns"""
        
        # Helper to check if an argument is potentially "tainted" (not a raw string literal)
        def is_tainted_arg(arg):
            if isinstance(arg, ast.JoinedStr): # f-string containing variables
                return True
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, (ast.Add, ast.Mod)): # string concatenation or % formatting
                return True
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'format': # .format()
                return True
            return False

        # Extract function name
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # 1. SQL Injection Sinks
        if func_name in ('execute', 'executemany', 'raw_query'):
            for arg in node.args:
                if is_tainted_arg(arg):
                    self._add_bug(
                        line=node.lineno,
                        category="sql_injection",
                        severity=self.SEVERITY_CRITICAL,
                        message="Potential SQL Injection vulnerability detected",
                        evidence=f"Using concatenated or formatted string in database '{func_name}' call. Use parameterized queries (?, %s).",
                        suggestion="cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
                    )

        # 2. Command Injection Sinks
        if func_name in ('system', 'popen', 'Popen', 'call', 'run', 'check_output'):
            for arg in node.args:
                if is_tainted_arg(arg):
                    self._add_bug(
                        line=node.lineno,
                        category="command_injection",
                        severity=self.SEVERITY_CRITICAL,
                        message="Potential OS Command Injection vulnerability",
                        evidence=f"Arbitrary variables passed to OS execution sink '{func_name}'.",
                        suggestion="Use subprocess with shell=False and pass arguments as a list."
                    )
        
        # 3. Code Execution / Deserialization Sinks
        if func_name in ('eval', 'exec', 'loads'):
            for arg in node.args:
                if not isinstance(arg, ast.Constant):
                    vuln_type = "Insecure Deserialization" if func_name == "loads" else "Arbitrary Code Execution"
                    self._add_bug(
                        line=node.lineno,
                        category="code_injection",
                        severity=self.SEVERITY_CRITICAL,
                        message=f"Potential {vuln_type} vulnerability",
                        evidence=f"Non-constant variable passed directly into dangerous sink '{func_name}'.",
                    )
    
    def _add_bug(self, line: int, category: str, severity: str, message: str, evidence: str, suggestion: Optional[str] = None):
        """Add a bug to the list"""
        self.bugs.append({
            "file": self.current_file,
            "function": self.current_function,
            "line": line,
            "category": category,
            "severity": severity,
            "message": message,
            "evidence": evidence,
            "suggestion": suggestion,
            "detector": "static_rules"
        })


class JavaStaticBugDetector:
    """Pattern-based static bug detector for Java code"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    # Regex patterns for Java bug detection
    PATTERNS = [
        # Empty catch block
        (r'catch\s*\([^)]+\)\s*\{\s*\}', 'empty_catch_block', SEVERITY_HIGH,
         "Empty catch block silently swallows exceptions"),
        
        # Catching generic Exception
        (r'catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}', 'swallowed_exception', SEVERITY_CRITICAL,
         "Catching Exception and ignoring it hides all errors"),
        
        # == comparison with strings (should use .equals())
        (r'"\w*"\s*==\s*\w+|(\w+)\s*==\s*"\w*"', 'string_equality', SEVERITY_HIGH,
         "Use .equals() for String comparison, not =="),
        
        # Null check after dereference
        (r'(\w+)\.[^;]+;\s*if\s*\(\s*\1\s*!=\s*null', 'null_check_after_deref', SEVERITY_HIGH,
         "Null check after object is already dereferenced"),
        
        # Return in finally block
        (r'finally\s*\{[^}]*return\s+', 'return_in_finally', SEVERITY_HIGH,
         "Return in finally block can suppress exceptions"),
        
        # Thread.sleep in synchronized block
        (r'synchronized[^{]*\{[^}]*Thread\.sleep', 'sleep_in_synchronized', SEVERITY_MEDIUM,
         "Thread.sleep() in synchronized block can cause deadlock"),
        
        # Comparing floats with ==
        (r'(float|double)\s+\w+[^;]*==', 'float_equality', SEVERITY_MEDIUM,
         "Comparing floating point numbers with == is unreliable"),
        
        # Empty if body
        (r'if\s*\([^)]+\)\s*\{\s*\}', 'empty_if_body', SEVERITY_LOW,
         "Empty if body - possible incomplete code"),
        
        # Infinite loop pattern
        (r'while\s*\(\s*true\s*\)\s*\{(?![^}]*break)', 'potential_infinite_loop', SEVERITY_MEDIUM,
         "while(true) without visible break - potential infinite loop"),
        
        # Hardcoded credentials
        (r'(password|passwd|pwd|secret|key)\s*=\s*"[^"]+"', 'hardcoded_credentials', SEVERITY_CRITICAL,
         "Hardcoded credentials detected"),
        
        # System.exit in library code
        (r'System\.exit\s*\(', 'system_exit_call', SEVERITY_MEDIUM,
         "System.exit() terminates JVM - avoid in library code"),
        
        # printStackTrace without logging
        (r'\.printStackTrace\s*\(\s*\)', 'print_stack_trace', SEVERITY_LOW,
         "printStackTrace() should be replaced with proper logging"),
         
        # Taint Analysis: SQL Injection
        (r'\.executeQuery\s*\(\s*".*"\s*\+\s*\w+.*', 'sql_injection', SEVERITY_CRITICAL,
         "Potential SQL Injection: Concatenated string in database query. Use PreparedStatement."),
         
        # Taint Analysis: Command Injection
        (r'Runtime\.getRuntime\(\)\.exec\s*\(\s*[^"]*\+\s*\w+.*', 'command_injection', SEVERITY_CRITICAL,
         "Potential Command Injection: User input concatenated into Runtime.exec() command."),
    ]
    
    def detect_bugs_in_code(self, code: str, filepath: str) -> List[Dict[str, Any]]:
        """Analyze Java code using regex patterns"""
        bugs = []
        lines = code.split('\n')
        
        for pattern, category, severity, message in self.PATTERNS:
            for match in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
                # Find line number
                line_num = code[:match.start()].count('\n') + 1
                
                bugs.append({
                    "file": filepath,
                    "function": self._find_enclosing_method(code, match.start()),
                    "line": line_num,
                    "category": category,
                    "severity": severity,
                    "message": message,
                    "evidence": match.group(0)[:100],
                    "detector": "static_rules_java"
                })
        
        return bugs
    
    def _find_enclosing_method(self, code: str, position: int) -> Optional[str]:
        """Find the method name containing the given position"""
        # Simple heuristic: find last method declaration before position
        pattern = r'(?:public|private|protected|static|\s)+\s+\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\{'
        
        last_method = None
        for match in re.finditer(pattern, code[:position]):
            last_method = match.group(1)
        
        return last_method


class JSStaticBugDetector:
    """Pattern-based static bug detector for JavaScript/TypeScript"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    PATTERNS = [
        (r'console\.log\(', 'console_log_usage', SEVERITY_LOW, "Remove console.log in production"),
        (r'debugger;', 'debugger_statement', SEVERITY_HIGH, "Debugger statement found"),
        (r'==\s*null', 'loose_equality_null', SEVERITY_MEDIUM, "Use === null or === undefined"),
        (r'var\s+\w+', 'var_usage', SEVERITY_LOW, "Prefer 'let' or 'const' over 'var'"),
        (r'eval\(', 'eval_usage', SEVERITY_CRITICAL, "Avoid using eval() - security risk"),
    ]
    
    def detect_bugs_in_code(self, code: str, filepath: str) -> List[Dict[str, Any]]:
        bugs = []
        for pattern, category, severity, message in self.PATTERNS:
            for match in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
                line_num = code[:match.start()].count('\n') + 1
                bugs.append({
                    "file": filepath,
                    "function": None,
                    "line": line_num,
                    "category": category,
                    "severity": severity,
                    "message": message,
                    "evidence": match.group(0)[:100],
                    "detector": "static_rules_js"
                })
        return bugs

class CppStaticBugDetector:
    """Pattern-based static bug detector for C/C++"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    PATTERNS = [
        (r'gets\(', 'gets_usage', SEVERITY_CRITICAL, "Never use gets() - buffer overflow risk"),
        (r'strcpy\(', 'strcpy_usage', SEVERITY_HIGH, "Use strncpy() to avoid buffer overflows"),
        (r'sprintf\(', 'sprintf_usage', SEVERITY_HIGH, "Use snprintf() to avoid buffer overflows"),
        (r'system\(', 'system_call', SEVERITY_HIGH, "Avoid system() calls if possible"),
        (r'malloc\(', 'malloc_usage', SEVERITY_LOW, "Consider using new/delete or smart pointers in C++"),
        (r'goto\s+\w+', 'goto_usage', SEVERITY_MEDIUM, "Avoid goto statements"),
    ]
    
    def detect_bugs_in_code(self, code: str, filepath: str) -> List[Dict[str, Any]]:
        bugs = []
        for pattern, category, severity, message in self.PATTERNS:
            for match in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
                line_num = code[:match.start()].count('\n') + 1
                bugs.append({
                    "file": filepath,
                    "function": None,
                    "line": line_num,
                    "category": category,
                    "severity": severity,
                    "message": message,
                    "evidence": match.group(0)[:100],
                    "detector": "static_rules_cpp"
                })
        return bugs

def detect_static_bugs(static_results: List[Dict], show_progress: bool = False) -> List[Dict[str, Any]]:
    """
    Run static bug detection on all analyzed files
    """
    all_bugs = []
    py_detector = StaticBugDetector()
    java_detector = JavaStaticBugDetector()
    js_detector = JSStaticBugDetector()
    cpp_detector = CppStaticBugDetector()
    
    if show_progress:
        try:
            from tqdm import tqdm
            file_iter = tqdm(static_results, desc="Static bug detection", unit="file")
        except ImportError:
            file_iter = static_results
    else:
        file_iter = static_results
    
    for file_info in file_iter:
        filepath = file_info.get('path', '')
        
        detector = None
        if filepath.endswith('.py'):
            detector = py_detector
        elif filepath.endswith('.java'):
            detector = java_detector
        elif filepath.endswith('.js') or filepath.endswith('.jsx') or filepath.endswith('.ts') or filepath.endswith('.tsx'):
            detector = js_detector
        elif filepath.endswith('.cpp') or filepath.endswith('.c') or filepath.endswith('.h'):
            detector = cpp_detector
            
        if detector:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                bugs = detector.detect_bugs_in_code(code, filepath)
                all_bugs.extend(bugs)
            except Exception as e:
                all_bugs.append({
                    "file": filepath,
                    "function": None,
                    "line": 0,
                    "category": "analysis_error",
                    "severity": "info",
                    "message": f"Could not analyze file: {e}",
                    "evidence": str(e),
                    "detector": "static_rules"
                })
    
    return all_bugs

