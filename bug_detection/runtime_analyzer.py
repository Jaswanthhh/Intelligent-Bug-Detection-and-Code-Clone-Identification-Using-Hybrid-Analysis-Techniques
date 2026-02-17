"""
Runtime Bug Analyzer - Analyzes dynamic testing results for bug patterns

Detects:
- Crash patterns and runtime exceptions
- Timeout issues (potential infinite loops)
- Non-deterministic behavior
- Memory-related issues
- Exception frequency analysis
"""

import re
from typing import List, Dict, Any, Optional
from collections import defaultdict

class RuntimeBugAnalyzer:
    """Analyzes dynamic testing results to detect runtime bugs"""
    
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    # Common exception patterns and their severity
    EXCEPTION_PATTERNS = {
        # Critical - crashes and security issues
        r'MemoryError': (SEVERITY_CRITICAL, "Memory exhaustion - possible memory leak or unbounded allocation"),
        r'RecursionError': (SEVERITY_CRITICAL, "Maximum recursion depth exceeded - infinite recursion"),
        r'SystemExit': (SEVERITY_HIGH, "Program called sys.exit()"),
        r'KeyboardInterrupt': (SEVERITY_LOW, "Program interrupted"),
        
        # High - logic errors
        r'ZeroDivisionError': (SEVERITY_HIGH, "Division by zero - missing input validation"),
        r'IndexError': (SEVERITY_HIGH, "Index out of bounds - array/list access error"),
        r'KeyError': (SEVERITY_HIGH, "Dictionary key not found - missing key validation"),
        r'AttributeError': (SEVERITY_HIGH, "Attribute access on wrong type - possible None dereference"),
        r'TypeError': (SEVERITY_HIGH, "Type mismatch - incorrect argument types"),
        r'ValueError': (SEVERITY_MEDIUM, "Invalid value - input validation issue"),
        r'AssertionError': (SEVERITY_MEDIUM, "Assertion failed - invariant violation"),
        
        # Medium - resource and IO issues
        r'FileNotFoundError': (SEVERITY_MEDIUM, "File not found - missing file or path issue"),
        r'PermissionError': (SEVERITY_MEDIUM, "Permission denied - file access issue"),
        r'IOError|OSError': (SEVERITY_MEDIUM, "IO/OS error - system resource issue"),
        r'ConnectionError|ConnectionRefused': (SEVERITY_MEDIUM, "Connection error - network issue"),
        r'TimeoutError': (SEVERITY_MEDIUM, "Operation timed out"),
        
        # Low - usually handled
        r'StopIteration': (SEVERITY_LOW, "Iterator exhausted"),
        r'ImportError|ModuleNotFoundError': (SEVERITY_MEDIUM, "Import failed - missing dependency"),
        r'NameError': (SEVERITY_HIGH, "Undefined variable - possible typo or scope issue"),
        r'UnboundLocalError': (SEVERITY_HIGH, "Variable referenced before assignment"),
        
        # Java exceptions
        r'NullPointerException': (SEVERITY_HIGH, "Null pointer dereference"),
        r'ArrayIndexOutOfBoundsException': (SEVERITY_HIGH, "Array index out of bounds"),
        r'ClassCastException': (SEVERITY_HIGH, "Invalid type cast"),
        r'IllegalArgumentException': (SEVERITY_MEDIUM, "Invalid argument"),
        r'IllegalStateException': (SEVERITY_MEDIUM, "Invalid state"),
        r'ConcurrentModificationException': (SEVERITY_HIGH, "Collection modified during iteration"),
        r'OutOfMemoryError': (SEVERITY_CRITICAL, "JVM out of memory"),
        r'StackOverflowError': (SEVERITY_CRITICAL, "Stack overflow - infinite recursion"),
    }
    
    def __init__(self):
        self.bugs = []
    
    def analyze_dynamic_results(self, dyn_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze dynamic testing results for runtime bugs
        
        Args:
            dyn_results: Output from scan_folder_dynamic
            
        Returns:
            List of detected runtime bugs
        """
        self.bugs = []
        
        for result in dyn_results:
            filepath = result.get('path', '')
            runs = result.get('runs', 0)
            anomalies = result.get('anomalies', [])
            
            if not anomalies:
                continue
            
            # Analyze each anomaly
            for anomaly in anomalies:
                self._analyze_anomaly(filepath, anomaly, runs, len(anomalies))
            
            # Check for patterns across all anomalies
            self._analyze_anomaly_patterns(filepath, anomalies, runs)
        
        return self.bugs
    
    def _analyze_anomaly(self, filepath: str, anomaly: Dict, total_runs: int, total_anomalies: int):
        """Analyze a single anomaly"""
        
        # Check for timeout
        if anomaly.get('timeout'):
            self._add_bug(
                filepath=filepath,
                category="timeout",
                severity=self.SEVERITY_HIGH,
                message="Execution timed out - possible infinite loop or very slow operation",
                evidence=f"Run {anomaly.get('run', '?')} timed out: {anomaly.get('error', 'unknown')}"
            )
            return
        
        # Analyze stderr for exception information
        stderr = anomaly.get('stderr', '')
        stdout = anomaly.get('stdout', '')
        returncode = anomaly.get('returncode', 0)
        
        # Check for known exception patterns
        exception_found = False
        for pattern, (severity, description) in self.EXCEPTION_PATTERNS.items():
            if re.search(pattern, stderr) or re.search(pattern, stdout):
                exception_found = True
                
                # Extract the actual error message
                error_match = re.search(rf'{pattern}[:\s]*([^\n]*)', stderr + stdout)
                error_detail = error_match.group(1).strip() if error_match else ""
                
                self._add_bug(
                    filepath=filepath,
                    category=f"runtime_{pattern.lower().replace('|', '_')}",
                    severity=severity,
                    message=description,
                    evidence=f"Run {anomaly.get('run', '?')}: {pattern}" + (f" - {error_detail}" if error_detail else "")
                )
        
        # Generic crash if no specific exception found
        if not exception_found and returncode != 0:
            self._add_bug(
                filepath=filepath,
                category="runtime_crash",
                severity=self.SEVERITY_HIGH,
                message=f"Program crashed with exit code {returncode}",
                evidence=f"Run {anomaly.get('run', '?')}: {stderr[:200] if stderr else 'No error message'}"
            )
    
    def _analyze_anomaly_patterns(self, filepath: str, anomalies: List[Dict], total_runs: int):
        """Analyze patterns across multiple anomalies"""
        
        # Calculate failure rate
        failure_rate = len(anomalies) / total_runs if total_runs > 0 else 0
        
        if failure_rate >= 1.0:
            self._add_bug(
                filepath=filepath,
                category="always_fails",
                severity=self.SEVERITY_CRITICAL,
                message="Program fails on every execution",
                evidence=f"Failed {len(anomalies)}/{total_runs} runs (100%)"
            )
        elif failure_rate >= 0.5:
            self._add_bug(
                filepath=filepath,
                category="frequent_failures",
                severity=self.SEVERITY_HIGH,
                message=f"Program fails frequently ({failure_rate*100:.0f}% of runs)",
                evidence=f"Failed {len(anomalies)}/{total_runs} runs"
            )
        elif failure_rate > 0:
            # Intermittent failures might indicate non-deterministic bugs
            self._add_bug(
                filepath=filepath,
                category="intermittent_failure",
                severity=self.SEVERITY_MEDIUM,
                message=f"Program fails intermittently ({failure_rate*100:.0f}% of runs)",
                evidence=f"Failed {len(anomalies)}/{total_runs} runs - possible race condition or input-dependent bug"
            )
        
        # Check for multiple different exception types
        exception_types = set()
        for anomaly in anomalies:
            stderr = anomaly.get('stderr', '') + anomaly.get('stdout', '')
            for pattern in self.EXCEPTION_PATTERNS.keys():
                if re.search(pattern, stderr):
                    exception_types.add(pattern)
        
        if len(exception_types) > 2:
            self._add_bug(
                filepath=filepath,
                category="multiple_exception_types",
                severity=self.SEVERITY_HIGH,
                message=f"Multiple different exception types detected ({len(exception_types)} types)",
                evidence=f"Exception types: {', '.join(exception_types)}"
            )
    
    def _add_bug(self, filepath: str, category: str, severity: str, message: str, evidence: str):
        """Add a bug to the list"""
        self.bugs.append({
            "file": filepath,
            "function": None,
            "line": 0,
            "category": category,
            "severity": severity,
            "message": message,
            "evidence": evidence,
            "detector": "runtime_analyzer"
        })


def analyze_runtime_bugs(dyn_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to analyze dynamic results for runtime bugs
    
    Args:
        dyn_results: Output from scan_folder_dynamic
        
    Returns:
        List of detected runtime bugs
    """
    analyzer = RuntimeBugAnalyzer()
    return analyzer.analyze_dynamic_results(dyn_results)

