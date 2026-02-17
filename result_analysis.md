# Full Result Analysis — Intelligent Bug Detection & Code Cloning System

> **Analysis Date**: 16 February 2026
> **Execution Time**: 38.15 seconds
> **Sample Folder**: `samples/` (25 files: Python, Java, C++, JavaScript)

---

## 1. Summary Statistics

| Metric | Value |
|---|---|
| **Total Files Scanned** | 25 |
| **Total Code Snippets Parsed** | 54 |
| **Total Bugs Detected** | 36 |
| **Total Clone Pairs Found** | 3 |
| **Files Dynamically Tested** | 9 |
| **Fusion Reports Generated** | 3 |
| **Average Semantic Similarity** | 1.00 |
| **Average Fusion Score** | 0.70 |
| **Files with Bugs** | 5 |
| **Files with Runtime Anomalies** | 0 |

---

## 2. Bug Detection Results

### 2.1 Severity Distribution

| Severity | Count | Percentage |
|---|---|---|
| 🔴 **Critical** | 5 | 13.9% |
| 🟠 **High** | 19 | 52.8% |
| 🟡 **Medium** | 9 | 25.0% |
| 🟢 **Low** | 3 | 8.3% |
| **Total** | **36** | **100%** |

### 2.2 Bug Category Breakdown

| Category | Count | Severity |
|---|---|---|
| Empty Exception Handler | 5 | High |
| Bare Except | 4 | High |
| Division by Zero | 3 | Critical |
| Shadowed Builtin | 3 | Medium |
| System Call (unsafe) | 2 | High |
| Strcpy Usage (buffer overflow) | 2 | High |
| Duplicate Condition | 2 | High |
| Constant Condition | 2 | Medium/High |
| Goto Usage | 2 | Medium |
| Unused Parameter | 2 | Low |
| Swallowed Exception | 1 | Critical |
| Always-False Condition | 1 | Critical |
| Always-True Condition (Tautology) | 1 | Medium |
| Self-Comparison (Always False) | 1 | High |
| Unreachable Code | 1 | High |
| Mutable Default Argument | 1 | High |
| Equality None Comparison | 1 | Medium |
| Missing Return Path | 1 | Medium |
| Malloc Usage (C++) | 1 | Low |

### 2.3 Detection Engine Breakdown

| Detector | Bugs Found |
|---|---|
| `static_rules` (Python) | 24 |
| `static_rules_cpp` (C++) | 7 |
| `logical_checker` (AST-based) | 5 |
| **Total** | **36** |

### 2.4 Top 5 Critical Bugs Found

| # | File | Line | Bug | Evidence |
|---|---|---|---|---|
| 1 | `sample_buggy.py` | 77 | Swallowed Exception | Catching broad `Exception` and ignoring it |
| 2 | `sample_buggy.py` | 110 | Always-False Condition | `x and not x` is always False |
| 3 | `sample_buggy.py` | 117 | Division by Zero | `10 / 0` → ZeroDivisionError |
| 4 | `test_vuln.py` | 10 | Division by Zero | `1 / 0` in try block |
| 5 | `test_vuln_fixed.py` | 11 | Division by Zero | Same pattern carried over |

---

## 3. Semantic Clone Detection Results

### 3.1 Clone Pairs Detected

| # | File A | Function A | File B | Function B | Similarity | Fusion Score |
|---|---|---|---|---|---|---|
| 1 | `exact_clone.py` | `add()` | `sample_safe_1.py` | `add()` | **1.00** | 0.65 |
| 2 | `test_vuln.py` | `bad_error_handling()` | `test_vuln_fixed.py` | `bad_error_handling()` | **1.00** | 0.80 |
| 3 | `test_vuln.py` | `safe_function()` | `test_vuln_fixed.py` | `safe_function()` | **1.00** | 0.65 |

### 3.2 Fusion Score Breakdown (Weighted Model)

The system uses: **Score = 0.3×Structural + 0.5×Semantic + 0.2×Dynamic**

| Clone Pair | Structural | Semantic | Dynamic | Fusion Score |
|---|---|---|---|---|
| `add()` ↔ `add()` | 0.50 | 1.00 | 0.00 | **0.65** |
| `bad_error_handling()` ↔ `bad_error_handling()` | 1.00 | 1.00 | 0.00 | **0.80** |
| `safe_function()` ↔ `safe_function()` | 0.50 | 1.00 | 0.00 | **0.65** |

---

## 4. Static Analysis Overview

### 4.1 Files by Language

| Language | Files | Notes |
|---|---|---|
| Python (.py) | 9 | Full AST parsing + feature extraction |
| Java (.java) | 8 | Full AST parsing via javalang |
| C++ (.cpp) | 4 | Basic pattern-based analysis |
| JavaScript (.js) | 4 | Basic pattern-based analysis |

### 4.2 Top Complex Files (by functions/methods)

| File | Functions/Methods | Max Complexity |
|---|---|---|
| `sample_buggy.py` | 15 | 9 statements, 3 branches |
| `com/.../SampleJava2.java` | 7 | 12 statements |
| `com/.../SampleJava1.java` | 6 | 11 statements |
| `math_utils.py` | 2 | 9 statements, 3 branches |
| `math_utils_clone.py` | 2 | 10 statements, 3 branches |

---

## 5. Dynamic Testing Results

| File | Runs | Anomalies |
|---|---|---|
| `buggy_critical.py` | 5 | 0 |
| `exact_clone.py` | 5 | 0 |
| `math_utils.py` | 5 | 0 |
| `math_utils_clone.py` | 5 | 0 |
| `sample_buggy.py` | 5 | 0 |
| `sample_safe_1.py` | 5 | 0 |
| `sample_safe_2.py` | 5 | 0 |
| `test_vuln.py` | 5 | 0 |
| `test_vuln_fixed.py` | 5 | 0 |

> **Note**: Dynamic fuzzer ran 5 iterations per file. No runtime crashes detected during fuzzing.

---

## 6. Screenshot Guide for Report

> **What screenshots should you take for the project report:**

### Terminal / CLI Screenshots
1. **Pipeline Execution** — Terminal showing `python main.py --code_folder samples` running with output
2. **Server Startup** — Terminal showing `python server.py` with Uvicorn running on port 8000
3. **Frontend Startup** — Terminal showing `npm run dev` on port 3000

### Dashboard (localhost:3000) Screenshots
4. **Home Page** — The landing page with file picker / GitHub URL input
5. **Analysis Loading** — The progress indicator while analysis runs
6. **Dashboard Overview** — Full dashboard with summary cards (Total Bugs, Clone Pairs, etc.)
7. **Bug List** — Scrolled view showing detected bugs with severity colors
8. **Bug Detail / Repair Dialog** — Click "Review Fix" on a bug → shows the "Suggested Patch" dialog
9. **Clone Pairs Section** — The semantic clone pairs with similarity scores
10. **Charts** — Any charts visible (severity pie chart, category bar chart)
11. **3D Galaxy Visualization** — The "Project Visualization" page with the 3D file galaxy

### API / Endpoint Screenshots
12. **API Docs** — Visit `http://localhost:8000/docs` (auto-generated Swagger UI)
13. **Health Check** — Browser showing `http://localhost:8000/health` → `{"status":"ok"}`

### VS Code Extension Screenshots
14. **Extension Running** — The Extension Host with a Python file open
15. **Bug Diagnostics** — Red/yellow squiggly underlines on detected bugs
16. **Repair Output** — The `_fixed.py` side-by-side diff view

### APR (Automated Bug Repair) Screenshots
17. **Original vs Fixed** — Side-by-side of `test_vuln.py` vs `test_vuln_fixed.py`

### JSON Output Screenshot
18. **JSON Results** — Open `full_results.json` showing the structured output
