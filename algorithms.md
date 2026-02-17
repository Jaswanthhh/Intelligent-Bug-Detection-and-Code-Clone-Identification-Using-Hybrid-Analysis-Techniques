# Project Algorithms

This document details the algorithms and methodologies used in the project for static analysis, dynamic analysis, semantic similarity, bug detection, and fusion scoring.

## 1. Static Analysis
**Location:** `static_analysis/ast_parser.py`, `bug_detection/static_rules.py`

The static analysis module extracts structural features from source code without executing it.

### Python Analysis
*   **Parser:** Uses Python's built-in `ast` module to generate an Abstract Syntax Tree (AST).
*   **Feature Extraction:**
    *   **Number of Statements:** Counts all nodes that are instances of `ast.stmt`.
    *   **Number of Branches:** Counts control flow nodes: `ast.If`, `ast.For`, `ast.While`, `ast.Try`.
*   **Bug Detection:** Traverses the AST to identify specific patterns (see [Bug Detection](#4-bug-detection)).

### Java Analysis
*   **Parser:** Uses `javalang` library (if available) to parse Java code.
*   **Feature Extraction:**
    *   **Number of Statements:** Counts the number of statements in a method's body.
    *   **Number of Branches:** Counts control flow structures within the method body.
*   **Bug Detection:** Uses regex-based pattern matching to identify issues like empty catch blocks or incorrect string comparisons.

## 2. Semantic Analysis
**Location:** `semantic_analysis/llm_embeddings.py`

This module calculates the semantic similarity between code snippets to identify potential clones or semantically related code.

### Embedding Generation
*   **Primary Method:** Uses `sentence-transformers` (Model: `all-MiniLM-L6-v2`) to generate dense vector embeddings for code snippets.
*   **Fallback Method:** If `sentence-transformers` is unavailable, uses `sklearn.feature_extraction.text.TfidfVectorizer` with character-level n-grams (1-3) to create sparse vectors.

### Similarity Calculation
*   **Metric:** Cosine Similarity between embedding vectors.
*   **Pairing:** Identifies pairs of code snippets where the similarity score exceeds a configurable `threshold` (default: 0.75).

## 3. Dynamic Analysis
**Location:** `dynamic_testing/rl_tester.py`, `bug_detection/runtime_analyzer.py`

The dynamic analysis module executes code in a controlled environment to observe runtime behavior.

### Execution Engine
*   **Method:** "Fuzzing-like" approach where code files are executed multiple times (default: 5 runs).
*   **Data Capture:** Captures `returncode`, `stdout`, and `stderr` for each execution.

### Anomaly Detection
*   **Anomalies:** Any execution with a non-zero return code or output to `stderr` is flagged as an anomaly.
*   **Pattern Analysis:**
    *   **Failure Rate:** Calculates the percentage of failed runs to categorize bugs (e.g., "Always Fails" vs. "Intermittent").
    *   **Exception Parsing:** Uses regex to identify specific Python exception types (e.g., `MemoryError`, `RecursionError`) and Java exceptions (e.g., `NullPointerException`) from `stderr`.

## 4. Bug Detection
**Location:** `bug_detection/`

The project employs a multi-layered bug detection strategy.

### A. Static Rules (`static_rules.py`)
*   **Python (AST-based):**
    *   Mutable default arguments
    *   Unused parameters
    *   Shadowed built-ins
    *   Unreachable code
    *   Bare `except:` clauses
    *   Empty exception handlers
    *   Suspicious comparisons (e.g., `== None`)
*   **Java (Regex-based):**
    *   Empty catch blocks
    *   String comparison using `==`
    *   Return statements in `finally` blocks
    *   Hardcoded credentials
    *   `System.exit()` calls

### B. Logical Checker (`logical_checker.py`)
*   **Contradictory Conditions:** Detects `if x` followed by `if not x` (implied) or explicit contradictions in boolean logic.
*   **Redundancy:** Identifies duplicate conditions or tautologies (e.g., `x or not x`).
*   **Docstring Consistency:** Verifies if "returns" or "raises" in docstrings match the actual function implementation.
*   **Self-Comparison:** Detects `x == x` (always true) or `x != x` (always false).

### C. Runtime Analyzer (`runtime_analyzer.py`)
*   **Crash Detection:** Identifies program crashes and exit codes.
*   **Timeout Detection:** Flags executions that exceed time limits (potential infinite loops).
*   **Resource Issues:** Detects `MemoryError`, `RecursionError`.
*   **Logic Errors:** Detects `ZeroDivisionError`, `IndexError`, `KeyError`, etc.

## 5. Fusion Scoring
**Location:** `classifier/fusion_model.py`

The fusion model combines multiple signals to produce a single "suspicion" or "importance" score for code pairs.

### Structural Similarity
*   Calculates the similarity between feature vectors (e.g., statement counts).
*   **Formula:** Average of `1.0 - abs(a - b) / (max(a, b) + 1e-6)` for each feature.

### Fusion Score Formula
Combines Structural Similarity, Semantic Similarity, and Dynamic Anomalies using a weighted sum:

```python
Score = (0.3 * Structural_Sim) + (0.5 * Semantic_Sim) + (0.2 * Dynamic_Anomaly_Flag)
```

*   **Weights:**
    *   Structural Similarity: 0.3
    *   Semantic Similarity: 0.5
    *   Dynamic Anomaly: 0.2 (Binary flag: 1.0 if anomalies exist, else 0.0)
