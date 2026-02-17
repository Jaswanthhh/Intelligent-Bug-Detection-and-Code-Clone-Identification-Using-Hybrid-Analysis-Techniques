"""
Main Bug Detector - Orchestrates all bug detection modules

Combines results from:
- Static rule-based detection
- Runtime/dynamic analysis
- Logical consistency checking
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from .static_rules import detect_static_bugs
from .runtime_analyzer import analyze_runtime_bugs
from .logical_checker import check_logical_bugs


class BugDetector:
    """
    Main bug detector that orchestrates all detection modules
    """
    
    SEVERITY_ORDER = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
        "info": 4
    }
    
    def __init__(self):
        self.bugs = []
        self.stats = {
            "total_bugs": 0,
            "by_severity": defaultdict(int),
            "by_category": defaultdict(int),
            "by_detector": defaultdict(int),
            "by_file": defaultdict(int)
        }
    
    def detect_all(self, 
                   static_results: List[Dict],
                   dyn_results: List[Dict],
                   snippet_records: List[Dict] = None,
                   show_progress: bool = False) -> List[Dict[str, Any]]:
        """
        Run all bug detection modules
        
        Args:
            static_results: Output from scan_code_folder
            dyn_results: Output from scan_folder_dynamic
            snippet_records: Optional snippet records for semantic analysis
            show_progress: Show progress bars
            
        Returns:
            List of all detected bugs, sorted by severity
        """
        self.bugs = []
        
        # 1. Static rule-based detection
        print("  [*] Running static bug detection...")
        static_bugs = detect_static_bugs(static_results, show_progress=show_progress)
        self.bugs.extend(static_bugs)
        print(f"      -> Found {len(static_bugs)} static bugs")
        
        # 2. Runtime/dynamic analysis
        print("  [*] Analyzing runtime behavior...")
        runtime_bugs = analyze_runtime_bugs(dyn_results)
        self.bugs.extend(runtime_bugs)
        print(f"      -> Found {len(runtime_bugs)} runtime bugs")
        
        # 3. Logical consistency checking
        print("  [*] Checking logical consistency...")
        logical_bugs = check_logical_bugs(static_results, show_progress=show_progress)
        self.bugs.extend(logical_bugs)
        print(f"      -> Found {len(logical_bugs)} logical bugs")
        
        # Deduplicate bugs
        self.bugs = self._deduplicate_bugs(self.bugs)
        
        # Sort by severity
        self.bugs.sort(key=lambda b: (
            self.SEVERITY_ORDER.get(b.get("severity", "info"), 99),
            b.get("file", ""),
            b.get("line", 0)
        ))
        
        # Calculate statistics
        self._calculate_stats()
        
        return self.bugs
    
    def _deduplicate_bugs(self, bugs: List[Dict]) -> List[Dict]:
        """Remove duplicate bug reports"""
        seen = set()
        unique_bugs = []
        
        for bug in bugs:
            # Create a unique key for the bug
            key = (
                bug.get("file", ""),
                bug.get("line", 0),
                bug.get("category", ""),
                bug.get("message", "")[:50]  # First 50 chars of message
            )
            
            if key not in seen:
                seen.add(key)
                unique_bugs.append(bug)
        
        return unique_bugs
    
    def _calculate_stats(self):
        """Calculate bug statistics"""
        self.stats = {
            "total_bugs": len(self.bugs),
            "by_severity": defaultdict(int),
            "by_category": defaultdict(int),
            "by_detector": defaultdict(int),
            "by_file": defaultdict(int)
        }
        
        for bug in self.bugs:
            self.stats["by_severity"][bug.get("severity", "unknown")] += 1
            self.stats["by_category"][bug.get("category", "unknown")] += 1
            self.stats["by_detector"][bug.get("detector", "unknown")] += 1
            self.stats["by_file"][bug.get("file", "unknown")] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bug statistics"""
        return {
            "total_bugs": self.stats["total_bugs"],
            "by_severity": dict(self.stats["by_severity"]),
            "by_category": dict(self.stats["by_category"]),
            "by_detector": dict(self.stats["by_detector"]),
            "files_with_bugs": len(self.stats["by_file"])
        }
    
    def get_critical_bugs(self) -> List[Dict]:
        """Get only critical and high severity bugs"""
        return [b for b in self.bugs if b.get("severity") in ("critical", "high")]
    
    def get_bugs_by_file(self, filepath: str) -> List[Dict]:
        """Get bugs for a specific file"""
        return [b for b in self.bugs if b.get("file") == filepath]
    
    def get_summary_report(self) -> str:
        """Generate a human-readable summary report"""
        lines = []
        lines.append("=" * 60)
        lines.append("BUG DETECTION SUMMARY")
        lines.append("=" * 60)
        
        lines.append(f"\nTotal Bugs Found: {self.stats['total_bugs']}")
        
        if self.stats['total_bugs'] == 0:
            lines.append("\n✓ No bugs detected!")
            return "\n".join(lines)
        
        # By severity
        lines.append("\nBy Severity:")
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = self.stats["by_severity"].get(severity, 0)
            if count > 0:
                marker = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]", "low": "[.]", "info": "[i]"}.get(severity, "")
                lines.append(f"  {marker} {severity.upper()}: {count}")
        
        # By detector
        lines.append("\nBy Detection Method:")
        for detector, count in sorted(self.stats["by_detector"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {detector}: {count}")
        
        # Top categories
        lines.append("\nTop Bug Categories:")
        sorted_categories = sorted(self.stats["by_category"].items(), key=lambda x: -x[1])[:10]
        for category, count in sorted_categories:
            lines.append(f"  - {category}: {count}")
        
        # Files with most bugs
        if self.stats["by_file"]:
            lines.append("\nFiles with Most Bugs:")
            sorted_files = sorted(self.stats["by_file"].items(), key=lambda x: -x[1])[:5]
            for filepath, count in sorted_files:
                lines.append(f"  - {filepath}: {count} bugs")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def detect_bugs(static_results: List[Dict],
                dyn_results: List[Dict],
                snippet_records: List[Dict] = None,
                show_progress: bool = False) -> tuple:
    """
    Convenience function to run all bug detection
    
    Args:
        static_results: Output from scan_code_folder
        dyn_results: Output from scan_folder_dynamic
        snippet_records: Optional snippet records
        show_progress: Show progress bars
        
    Returns:
        Tuple of (bugs_list, stats_dict, summary_report_string)
    """
    detector = BugDetector()
    bugs = detector.detect_all(static_results, dyn_results, snippet_records, show_progress)
    stats = detector.get_stats()
    summary = detector.get_summary_report()
    
    return bugs, stats, summary

def propagate_bugs_by_clones(bugs: List[Dict], clone_reports: List[Dict]) -> List[Dict]:
    """
    Propagate bugs across detected clones.
    If File A has a bug, and File B is a clone of File A, flag File B.
    """
    new_bugs = []
    # Index bugs by file and function
    bug_map = defaultdict(list)
    for b in bugs:
        # Key: (file, function_name)
        key = (b.get("file"), b.get("function"))
        bug_map[key].append(b)
        
    for report in clone_reports:
        # Check A -> B
        file_a = report.get("file_a")
        func_a = report.get("func_a")
        file_b = report.get("file_b")
        func_b = report.get("func_b")
        fusion_score = report.get("fusion_score", 0)
        
        # Only propagate if similarity is high
        if fusion_score < 0.7:
            continue
            
        # If A has bugs, propagate to B
        if (file_a, func_a) in bug_map:
            for source_bug in bug_map[(file_a, func_a)]:
                # Avoid duplicates if B already has this bug
                if any(b.get("message") == source_bug.get("message") for b in bug_map.get((file_b, func_b), [])):
                    continue
                    
                propagated_bug = {
                    "file": file_b,
                    "line": 0, # Don't know exact line in B, assume top of file/func
                    "function": func_b,
                    "severity": "medium", # Lower severity for propagated bugs till verified
                    "category": "Propagated Bug",
                    "detector": "Clone Propagation",
                    "message": f"Potential bug propagated from clone {file_a} (Source: {source_bug.get('message')})",
                    "evidence": f"Clone similarity: {fusion_score:.2f} with {file_a}:{func_a}"
                }
                new_bugs.append(propagated_bug)
                
        # If B has bugs, propagate to A (Bidirectional)
        if (file_b, func_b) in bug_map:
            for source_bug in bug_map[(file_b, func_b)]:
                if any(b.get("message") == source_bug.get("message") for b in bug_map.get((file_a, func_a), [])):
                    continue
                    
                propagated_bug = {
                    "file": file_a,
                    "line": 0,
                    "function": func_a,
                    "severity": "medium",
                    "category": "Propagated Bug",
                    "detector": "Clone Propagation",
                    "message": f"Potential bug propagated from clone {file_b} (Source: {source_bug.get('message')})",
                    "evidence": f"Clone similarity: {fusion_score:.2f} with {file_b}:{func_b}"
                }
                new_bugs.append(propagated_bug)
                
    return new_bugs

