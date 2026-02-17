"""
BCI (Bytecode Instrumentation) Integration for Java Code Analysis
Provides execution trace collection using bci_injector.jar
"""
import os
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class JavaTraceCollector:
    def __init__(self, bci_jar_path: str, config_dir: str = "bci_conf", output_dir: str = "experiments/java-traces"):
        self.bci_jar_path = bci_jar_path
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        Path(self.config_dir).mkdir(exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_inclusion_filter(self, java_files: List[str], filter_name: str = "bci_java.txt") -> str:
        """
        Create inclusion filter file based on Java files found
        Extracts package names and class names from Java files
        """
        filter_path = os.path.join(self.config_dir, filter_name)
        packages = set()
        classes = set()
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract package declarations
                import re
                package_match = re.search(r'package\s+([a-zA-Z_][a-zA-Z0-9_.]*);', content)
                if package_match:
                    packages.add(package_match.group(1))
                
                # Extract class names
                class_matches = re.findall(r'(?:public\s+)?(?:class|interface|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                for class_name in class_matches:
                    if package_match:
                        full_class = f"{package_match.group(1)}.{class_name}"
                    else:
                        full_class = class_name
                    classes.add(full_class)
                    
            except Exception as e:
                print(f"Warning: Could not parse {java_file}: {e}")
        
        # Write inclusion filter
        with open(filter_path, 'w') as f:
            f.write("# BCI Inclusion Filter - Auto-generated\n")
            f.write("# Package instrumentation\n")
            for pkg in sorted(packages):
                f.write(f"package:{pkg}\n")
            
            f.write("\n# Class instrumentation\n")
            for cls in sorted(classes):
                f.write(f"class:{cls}\n")
        
        return filter_path
    
    def run_java_with_bci(self, java_file: str, main_class: str = None, 
                         debug_logs: bool = False, write_after_events: int = 1) -> Dict[str, Any]:
        """
        Run Java file with BCI instrumentation
        
        Args:
            java_file: Path to Java file to execute
            main_class: Main class name (if different from filename)
            debug_logs: Enable debug logging
            write_after_events: Number of events before writing to file
            
        Returns:
            Dictionary with execution results and trace file path
        """
        if not os.path.exists(self.bci_jar_path):
            raise FileNotFoundError(f"BCI jar not found at {self.bci_jar_path}")
        
        # Create inclusion filter
        filter_path = self.create_inclusion_filter([java_file])
        
        # Generate trace file name
        timestamp = int(time.time())
        trace_file = os.path.join(self.output_dir, f"trace_{timestamp}.csv")
        
        # Determine main class
        if main_class is None:
            main_class = Path(java_file).stem
        
        # Build Java command with BCI agent
        java_cmd = [
            "java",
            f"-javaagent:{self.bci_jar_path}={filter_path};{trace_file};{str(debug_logs).lower()};{write_after_events}",
            main_class
        ]
        
        print(f"Running Java with BCI: {' '.join(java_cmd)}")
        
        try:
            # Compile Java file first
            compile_result = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(java_file) or "."
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Compilation failed: {compile_result.stderr}",
                    "trace_file": None
                }
            
            # Run with BCI
            result = subprocess.run(
                java_cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(java_file) or ".",
                timeout=30  # 30 second timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "trace_file": trace_file if os.path.exists(trace_file) else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out",
                "trace_file": trace_file if os.path.exists(trace_file) else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "trace_file": None
            }
    
    def analyze_trace_file(self, trace_file: str) -> Dict[str, Any]:
        """
        Analyze BCI trace file and extract execution patterns
        """
        if not os.path.exists(trace_file):
            return {"error": "Trace file not found"}
        
        try:
            with open(trace_file, 'r') as f:
                lines = f.readlines()
            
            # Parse trace data (format depends on BCI output)
            events = []
            for line in lines:
                if line.strip():
                    # Basic CSV parsing - adjust based on actual BCI output format
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        events.append({
                            "timestamp": parts[0] if len(parts) > 0 else "",
                            "class": parts[1] if len(parts) > 1 else "",
                            "method": parts[2] if len(parts) > 2 else "",
                            "details": parts[3:] if len(parts) > 3 else []
                        })
            
            # Analyze patterns
            class_counts = {}
            method_counts = {}
            call_sequences = []
            
            for event in events:
                class_name = event.get("class", "")
                method_name = event.get("method", "")
                
                if class_name:
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                if method_name:
                    method_counts[method_name] = method_counts.get(method_name, 0) + 1
                
                call_sequences.append(f"{class_name}.{method_name}")
            
            return {
                "total_events": len(events),
                "class_counts": class_counts,
                "method_counts": method_counts,
                "call_sequences": call_sequences,
                "events": events
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze trace file: {str(e)}"}

def scan_java_folder_with_bci(folder_path: str, bci_jar_path: str) -> List[Dict[str, Any]]:
    """
    Scan folder for Java files and run BCI analysis on each
    """
    collector = JavaTraceCollector(bci_jar_path)
    results = []
    
    # Find all Java files
    java_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    
    print(f"Found {len(java_files)} Java files to analyze")
    
    for java_file in java_files:
        print(f"Analyzing {java_file}...")
        result = collector.run_java_with_bci(java_file)
        
        if result["success"] and result["trace_file"]:
            trace_analysis = collector.analyze_trace_file(result["trace_file"])
            result["trace_analysis"] = trace_analysis
        
        result["java_file"] = java_file
        results.append(result)
    
    return results

def scan_paths_with_bci(paths: List[str], bci_jar_path: str) -> List[Dict[str, Any]]:
    """
    Scan list of paths for Java files and run BCI analysis on each
    """
    collector = JavaTraceCollector(bci_jar_path)
    results = []
    
    # Ensure paths is a list
    if isinstance(paths, str):
        paths = [paths]
    
    # Find all Java files
    java_files = []
    for path in paths:
        if os.path.isfile(path):
            if path.endswith('.java'):
                java_files.append(path)
        else:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.java'):
                        java_files.append(os.path.join(root, file))
    
    print(f"Found {len(java_files)} Java files to analyze")
    
    for java_file in java_files:
        print(f"Analyzing {java_file}...")
        result = collector.run_java_with_bci(java_file)
        
        if result["success"] and result["trace_file"]:
            trace_analysis = collector.analyze_trace_file(result["trace_file"])
            result["trace_analysis"] = trace_analysis
        
        result["java_file"] = java_file
        results.append(result)
    
    return results

if __name__ == "__main__":
    # Test the collector
    bci_jar = "bci_injector.jar"  # Place BCI jar in project root
    if os.path.exists(bci_jar):
        results = scan_java_folder_with_bci("samples", bci_jar)
        print(f"BCI analysis completed for {len(results)} files")
        for result in results:
            print(f"File: {result['java_file']}")
            print(f"Success: {result['success']}")
            if result.get('trace_file'):
                print(f"Trace file: {result['trace_file']}")
    else:
        print(f"BCI jar not found at {bci_jar}")
        print("Please download bci_injector.jar and place it in the project root")

