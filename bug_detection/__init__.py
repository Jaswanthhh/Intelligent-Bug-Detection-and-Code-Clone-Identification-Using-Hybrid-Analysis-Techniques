"""
Bug Detection Module for Code Analysis Pipeline

Detects:
- Correctness/semantic bugs
- Logical bugs
- Crash/runtime exception patterns
- Incorrect error/exception handling
- Logical contradictions
"""

from .detector import BugDetector, detect_bugs
from .static_rules import StaticBugDetector
from .runtime_analyzer import RuntimeBugAnalyzer
from .logical_checker import LogicalBugChecker

__all__ = ['BugDetector', 'detect_bugs', 'StaticBugDetector', 'RuntimeBugAnalyzer', 'LogicalBugChecker']

