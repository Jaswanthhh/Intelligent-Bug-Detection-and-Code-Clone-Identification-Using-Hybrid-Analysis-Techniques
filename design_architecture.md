# Design and Architecture

## 1. System Architecture Overview
The system is architected as a sequential pipeline that progressively enriches the understanding of the input code. It is designed to be modular, allowing individual components (like the LLM model or the Fuzzer) to be swapped or upgraded without affecting the whole.

### High-Level Architecture Diagram
```mermaid
graph TD
    subgraph "Layer 1: Input Processing"
        Src[Source Code] --> Filter[File Filter]
        Filter --> Parsers[Polyglot Parsers]
    end

    subgraph "Layer 2: Analysis Engines"
        Parsers --> Static[Static Analyzer (AST)]
        Parsers --> Semantic[Semantic Analyzer (LLM)]
        Parsers --> Dynamic[Dynamic Analyzer (BCI/Fuzz)]
    end

    subgraph "Layer 3: Data Representation"
        Static --> StructDB[(Structural Features)]
        Semantic --> VectorDB[(Vector Embeddings)]
        Dynamic --> TraceDB[(Execution Logs)]
    end

    subgraph "Layer 4: Intelligence & Fusion"
        StructDB & VectorDB & TraceDB --> Fusion[Fusion Engine]
        Fusion --> Classifier[Bug/Clone Classifier]
    end

    subgraph "Layer 5: Reporting"
        Classifier --> JSON[JSON Output]
        Classifier --> HTML[HTML Dashboard]
    end
```

## 2. Component Details

### 2.1 Static Analysis Module
**Goal**: Extract structural fingerprints.
- **Technology**: Python `ast` module for Python, `javalang` for Java.
- **Process**:
    1.  Walk the directory tree.
    2.  Parse each file into an Abstract Syntax Tree (AST).
    3.  Extract functions/methods.
    4.  Compute metrics: Cyclomatic Complexity, Line Count, Parameter Count.
- **Output**: A dictionary of structural features for every function.

### 2.2 Semantic Analysis Module
**Goal**: Understand code intent.
- **Technology**: `sentence-transformers` (Hugging Face), Model: `all-MiniLM-L6-v2`.
- **Process**:
    1.  Preprocess code (remove comments, normalize whitespace).
    2.  Pass code text through the Transformer model.
    3.  Generate a 384-dimensional dense vector.
    4.  Compute Cosine Similarity matrix for all pairs.
- **Output**: A list of candidate pairs with high semantic similarity.

### 2.3 Dynamic Analysis Module
**Goal**: Verify behavior and find crashes.
- **Sub-module A: Fuzzing (Python)**
    - Uses `atheris` or custom randomized inputs.
    - Monitors for unhandled exceptions.
- **Sub-module B: BCI (Java)**
    - **Bytecode Instrumentation**: Uses a Java Agent (`premain`).
    - **ASM/Javassist**: Modifies bytecode at load time to inject logging calls at method entry/exit.
    - **Trace Collection**: Logs execution paths to CSV files.
- **Output**: A map of `File -> [Anomalies, ExecutionCounts]`.

### 2.4 Fusion Engine
**Goal**: Combine signals to make a decision.
- **Algorithm**:
    ```python
    FusionScore = (0.3 * StructuralSim) + (0.5 * SemanticSim) + (0.2 * DynamicAnomaly)
    ```
- **Logic**:
    - If Semantic Score is high (>0.8) but Structural is low (<0.2), it's likely a **Type 4 Clone**.
    - If Semantic Score is high AND Dynamic Anomaly is present in one but not the other, it's a **Latent Bug**.

## 3. Data Flow
1.  **Ingestion**: User points to a folder.
2.  **Parallel Processing**: Static and Semantic analysis run concurrently.
3.  **Dynamic Trigger**: Dynamic analysis runs on the top candidate files to save resources.
4.  **Aggregation**: Results are merged by File ID / Function Name.
5.  **Presentation**: Final report highlights "Critical" issues first.
