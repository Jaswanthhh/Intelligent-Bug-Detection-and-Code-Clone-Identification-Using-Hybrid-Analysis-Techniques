"""
CI/CD Runner Script
Wraps main.py to enforce quality gates in automated pipelines.
Exits with code 1 if CRITICAL bugs are found, blocking the build.
"""

import sys
import subprocess
import json
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python ci_runner.py <folder_to_analyze>")
        sys.exit(1)
        
    target_folder = sys.argv[1]
    output_file = "ci_results.json"
    
    print(f"[CI] Starting Analysis on: {target_folder}")
    
    # Run the main analysis
    cmd = [sys.executable, "main.py", "--code_folder", target_folder, "--output_json", output_file]
    
    # Pass through other flags if needed
    if "--evolution" in sys.argv:
        cmd.append("--evolution")
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        print("[CI] Analysis failed to execute!")
        print(result.stderr)
        sys.exit(result.returncode)
        
    # Check results
    if not os.path.exists(output_file):
        print("[CI] No results generated.")
        sys.exit(1)
        
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        bugs = data.get("bug_detection", {}).get("bugs", [])
        critical_bugs = [b for b in bugs if b.get("severity") == "critical"]
        
        print("-" * 50)
        print(f"[CI] Analysis Complete.")
        print(f"[CI] Total Bugs: {len(bugs)}")
        print(f"[CI] Critical Bugs: {len(critical_bugs)}")
        print("-" * 50)
        
        if critical_bugs:
            print("[!] BUILD FAILED: Critical bugs detected!")
            for b in critical_bugs:
                print(f"    - {b.get('file')}:{b.get('line')} - {b.get('message')}")
            sys.exit(1) # Fail the build
            
        print("[+] BUILD PASSED: No critical issues found.")
        sys.exit(0)
        
    except Exception as e:
        print(f"[CI] Error parsing results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
