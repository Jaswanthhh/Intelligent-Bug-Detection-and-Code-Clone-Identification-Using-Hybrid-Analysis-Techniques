# Problem Definition

## 1. The Core Problem
Modern software systems are massive, often containing millions of lines of code. Manual review is no longer feasible.
- **The "Copy-Paste" Culture**: Developers under deadline pressure often copy code. This leads to **Code Bloat** and **Inconsistent Logic**.
- **The "Silent Bug"**: Static analysis tools are good at finding syntax errors (e.g., missing semicolons), but they fail at finding *semantic* bugs (e.g., a sorting algorithm that doesn't sort correctly in edge cases).

## 2. Limitations of Existing Solutions
Current industry tools typically fall into one of two isolated categories:

### 2.1 Static Analysis Tools (e.g., SonarQube)
- **Pros**: Fast, covers 100% of the code.
- **Cons**: High False Positive rate. They flag "potential" issues that aren't actually bugs. They cannot see runtime values.
- **Failure Mode**: Cannot detect Type 4 (Semantic) clones because they look at *structure*, not *meaning*.

### 2.2 Dynamic Analysis Tools (e.g., Fuzzers)
- **Pros**: Finds real crashes (True Positives).
- **Cons**: Slow. Requires executable code and test cases. Can only test paths that are actually executed (low coverage).
- **Failure Mode**: Cannot tell you *why* the bug happened, only that it crashed.

## 3. Our Novelty: The Hybrid Fusion Model
We propose a **Multi-Modal Analysis Pipeline** that bridges the gap between static and dynamic analysis.

### 3.1 How We Address the Problem
Instead of relying on a single signal, we fuse three distinct signals:
1.  **Structural Signal (AST)**: "Does the code *look* similar?" (Good for Type 1-3 Clones).
2.  **Semantic Signal (LLM Embeddings)**: "Does the code *mean* the same thing?" (Good for Type 4 Clones).
3.  **Dynamic Signal (Behavioral Traces)**: "Does the code *act* the same way?" (Verification).

### 3.2 Key Innovations
- **Intelligent Embeddings**: Using Large Language Models (LLMs) to vectorize code allows us to match logic even if the syntax is completely different.
- **Bytecode Instrumentation (BCI)**: We don't just guess what the code does; we inject probes into the running application (Java) to record the exact execution flow.
- **Fusion Scoring**: A weighted algorithm that combines these inputs. A pair of functions is only flagged as a clone if they look similar AND act similar, drastically reducing false positives.

## 4. Summary of Contribution
| Feature | Traditional Static | Traditional Dynamic | **Our Hybrid Approach** |
| :--- | :--- | :--- | :--- |
| **Syntax Checks** | Yes | No | **Yes** |
| **Semantic Clones** | No | No | **Yes (via LLM)** |
| **Runtime Verification**| No | Yes | **Yes (via BCI)** |
| **False Positive Rate**| High | Low | **Very Low** |
