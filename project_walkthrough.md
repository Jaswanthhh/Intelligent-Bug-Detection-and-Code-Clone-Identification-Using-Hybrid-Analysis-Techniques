# Project Walkthrough: Intelligent Bug Detection and Code Cloning System

This document provides a complete start-to-end guide to understanding, running, and interpreting the results of the Intelligent Bug Detection and Code Cloning System.

## 1. Project Overview

**Goal:** To build a robust system that detects code clones (duplicates) and software bugs across multiple programming languages (Python and Java) using a hybrid approach.

**Key Features:**
*   **Multi-Language Support:** Analyzes both Python (`.py`) and Java (`.java`) files.
*   **Hybrid Analysis:** Combines three powerful techniques:
    1.  **Static Analysis:** Checks code structure without running it.
    2.  **Semantic Analysis:** Uses AI (Deep Learning) to understand what the code *does*.
    3.  **Dynamic Analysis:** Runs the code (Fuzzing) to find runtime crashes and errors.
*   **Fusion Engine:** intelligently combines these signals to give a final "Suspicion Score".
*   **Visual Reporting:** Generates diagrams (AST) and detailed reports.

---

## 2. System Architecture

The system is organized into 5 logical layers:

1.  **Input Layer:** Reads your source code folder.
2.  **Analysis Layer:**
    *   *Parsers* break down code into trees (AST).
    *   *AI Models* convert code into math vectors (Embeddings).
    *   *Fuzzers* execute code with random inputs.
3.  **Data Layer:** Stores features, vectors, and execution logs.
4.  **Intelligence Layer:** The "Fusion Engine" weighs the evidence to decide if code is a clone or buggy.
5.  **Reporting Layer:** Outputs JSON data, Markdown reports, and Diagrams.

---

## 3. Detailed Workflow (Step-by-Step)

When you run the project, the following pipeline executes:

### Step 1: Static Analysis
*   **What it does:** Scans every file in the `--code_folder`.
*   **How:**
    *   For **Python**: Uses the `ast` module to count loops, if-statements, and variables.
    *   For **Java**: Uses `javalang` to parse classes and methods.
*   **Output:** A list of functions/methods and their structural features (e.g., "Function A has 5 loops").

### Step 2: Semantic Analysis (AI)
*   **What it does:** Understands the meaning of the code.
*   **How:**
    *   Uses a pre-trained AI model (`all-MiniLM-L6-v2`).
    *   Converts code text into a 384-dimensional vector.
    *   Calculates **Cosine Similarity** between every pair of functions.
*   **Output:** Pairs of code that "mean" the same thing, even if written differently.

### Step 3: Dynamic Analysis (Fuzzing)
*   **What it does:** Checks if the code crashes.
*   **How:**
    *   Actually **runs** the code files (default: 5 times) in a safe subprocess.
    *   Captures errors (like `ZeroDivisionError` or `NullPointerException`).
*   **Output:** A list of "Anomalies" (crashes/errors) for each file.

### Step 4: Bug Detection
*   **What it does:** Applies specific rules to find common mistakes.
*   **How:**
    *   **Static Rules:** Checks for things like empty `catch` blocks or unused variables.
    *   **Runtime Rules:** Flags files that crashed during Step 3.
    *   **Logical Rules:** Looks for contradictions (e.g., `if x and not x`).
*   **Output:** A list of specific bugs with severity levels (Critical, High, Medium).

### Step 5: Fusion & Reporting
*   **What it does:** Makes the final decision.
*   **How:**
    *   Combines scores: `0.3 * Structure + 0.5 * Semantics + 0.2 * Dynamic`.
*   **Output:**
    *   `results.json`: Raw data for all steps.
    *   Console Output: Summary of top clones and bugs.
    *   Diagrams: Visual representations of the code structure.

---

## 4. How to Run the Project

### Prerequisites
Ensure you have Python installed. You can install dependencies using:
```bash
pip install numpy scikit-learn sentence-transformers tqdm javalang
```

### Basic Command
To run the full pipeline on the `samples` folder:
```bash
python main.py --code_folder samples --output_json results.json
```

### Common Options
*   `--semantic_threshold 0.75`: Only show clones with >75% similarity.
*   `--dynamic_runs 5`: Run each file 5 times to check for stability.
*   `--enable_bci`: Enable advanced Java tracing (requires `bci_injector.jar`).
*   `--visualize`: Generate flow diagrams for the code.
*   `--verbose`: Show more detailed logs.

### Using the Batch Script (Windows)
You can simply double-click `run_project.bat` or run it from the terminal:
```cmd
run_project.bat
```
This script automatically installs dependencies and runs 4 different scenarios for you.

---

## 5. Understanding the Output

### Console Output
*   **Summary Statistics:** Total files scanned, clones found, bugs detected.
*   **Top Candidates:** The most likely code clones.
*   **Detailed Bug Report:** Specific lines of code that need fixing.

### `results.json`
A machine-readable file containing:
*   `static_analysis`: Raw features for every file.
*   `semantic_analysis`: Similarity scores for code pairs.
*   `fusion_reports`: Final ranked list of clones.
*   `bug_detection`: List of all identified bugs.

### Visualizations
If you run with `--visualize`, the system generates `.mmd` (Mermaid) files. You can view these diagrams to see the control flow of your code (e.g., how data moves through `if` statements and loops).
