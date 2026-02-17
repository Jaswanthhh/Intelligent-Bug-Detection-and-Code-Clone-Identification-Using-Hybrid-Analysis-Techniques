from main import run_pipeline
import json
import os

paths = [
    os.path.abspath("samples/buggy.cpp"),
    os.path.abspath("samples/buggy.js")
]

print(f"Testing paths: {paths}")

try:
    results = run_pipeline(paths, enable_bug_detection=True, verbose=True)
    bugs = results.get("bugs", [])
    print(f"Found {len(bugs)} bugs")
    for b in bugs:
        print(f"- {b['file']}: {b['category']} ({b['severity']})")
except Exception as e:
    print(f"Error: {e}")
