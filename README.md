# Intelligent Bug Detection and Code Cloning System

## 1. Project Overview

**Goal:** To build a robust system that detects code clones (duplicates) and software bugs across multiple programming languages (Python and Java) using a hybrid approach. This project addresses the limitations of traditional static analysis tools by incorporating semantic understanding (AI) and dynamic verification (Fuzzing/BCI).

### Key Features
*   **Multi-Language Support:** Analyzes both Python (`.py`) and Java (`.java`) files.
*   **Hybrid Analysis Engine:**
    1.  **Static Analysis:** Structural checks (AST parsing).
    2.  **Semantic Analysis:** AI-powered code similarity (using `all-MiniLM-L6-v2` LLM).
    3.  **Dynamic Analysis:** Runtime verification via Fuzzing and Bytecode Instrumentation (BCI).
*   **Fusion Logic:** A weighted scoring system that combines structural, semantic, and dynamic signals to reduce false positives.
*   **Visual Reporting:** Generates AST diagrams and detailed JSON/Console reports.
*   **Bug Propagation:** Identifies latent bugs by tracing clone relationships.

---

## 2. System Architecture

The project is organized into modular components:

### Directory Structure
*   `static_analysis/`: AST parsers for Python and Java.
*   `semantic_analysis/`: LLM-based code embedding and similarity matching.
*   `dynamic_testing/`: Fuzzing logic and test execution.
*   `bci_tracing/`: Java Bytecode Instrumentation (BCI) for runtime tracing.
*   `classifier/`: Fusion model to combine analysis results.
*   `bug_detection/`: Logic for identifying specific bug patterns and propagating them.
*   `visualization/`: Tools to generate AST diagrams.
*   `samples/`: Default directory for test code.

### Pipeline Workflow (`main.py`)
1.  **Input:** User provides a code folder.
2.  **Static Analysis:** Scans files, extracts AST features (loops, conditionals), and builds snippets.
3.  **Semantic Analysis:** Computes embeddings for snippets and finds similar pairs using Cosine Similarity.
4.  **Dynamic Testing:**
    *   **Fuzzing:** Randomly executes functions to find crashes.
    *   **BCI (Java only):** Injects probes to trace execution flow if enabled.
5.  **Fusion:** Combines Static (30%), Semantic (50%), and Dynamic (20%) scores.
6.  **Reporting:** Outputs results to Console and JSON.

---

## 3. Installation & Requirements

### Prerequisites
*   Python 3.7+
*   Java JDK (for Java analysis and BCI)

### Dependencies
Install required Python packages:
```bash
pip install numpy scikit-learn sentence-transformers tqdm javalang fastapi uvicorn pydantic
```

*   `numpy`, `scikit-learn`: Data processing.
*   `sentence-transformers`: Semantic analysis (LLM).
*   `javalang`: Java parsing.
*   `fastapi`, `uvicorn`: API backend (if applicable).

---

## 4. Usage Guide

### Basic Command
Run the full pipeline on a folder:
```bash
python main.py --code_folder samples --output_json results.json
```

### Advanced Options
*   **Enable BCI (Java):**
    ```bash
    python main.py --code_folder samples --enable_bci --bci_jar bci_injector.jar
    ```
*   **Adjust Sensitivity:**
    ```bash
    python main.py --semantic_threshold 0.8 --dynamic_runs 10
    ```
*   **Visualize Code Structure:**
    ```bash
    python main.py --visualize
    ```

### Arguments
*   `--code_folder`: Path to source code.
*   `--semantic_threshold`: Similarity cutoff (0.0-1.0, default 0.75).
*   `--dynamic_runs`: Number of execution attempts per file (default 5).
*   `--enable_bci`: Turn on Java Bytecode Instrumentation.
*   `--visualize`: Generate `.mmd` diagrams (Mermaid format).
*   `--evolution`: Analyze Git history for bug evolution (if in a repo).

---

## 5. Understanding Outputs

### Console Output
*   **Summary Statistics:** Total files, clones found, bugs detected.
*   **Top Candidates:** detailed list of the most similar code pairs.
*   **Bug Reports:** Specific bugs with severity (Critical, High, Medium, Low).
*   **Dynamic Anomalies:** Files that crashed during testing.

### JSON Report (`results.json`)
Contains raw data for integration or further analysis:
*   `static_analysis`: AST feature vectors.
*   `semantic_analysis`: Similarity scores for pairs.
*   `fusion_reports`: Final combined scores and explanations.
*   `bug_detection`: List of detected bugs and their locations.
*   `bci_tracing`: Execution traces (if enabled).

---

## 6. Technical Components

*   **Embeddings:** Uses `sentence-transformers` (Pre-trained `all-MiniLM-L6-v2`) to convert code to vectors.
*   **BCI Injector:** A custom Java agent (`bci_injector.jar`) that attaches to the JVM to record method entries/exits.
*   **Git Evolution:** Can analyze commit history to track how bugs evolved over time.

For more details on specific components, refer to:
*   `BCI_INTEGRATION.md`: For BCI setup and usage.
*   `project_walkthrough.md`: For a step-by-step guide.
