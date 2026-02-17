# System Architecture Diagram

This document contains the updated system architecture diagram for the **Intelligent Bug Detection and Code Cloning System**, reflecting the latest features including Multi-Language Support (Python & Java) and Bytecode Instrumentation (BCI).

## Mermaid Diagram Code

You can copy the code below and render it using any Mermaid-compatible viewer (e.g., [Mermaid Live Editor](https://mermaid.live/), VS Code with Mermaid extension).

```mermaid
graph TD
    %% Styling
    classDef storage fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef input fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    %% Layer 1: Input Processing
    subgraph "Layer 1: Input Processing"
        Src[Source Code Folder]:::input --> Filter[File Filter]:::process
        Filter -->|Python Files| PyParser[Python AST Parser]:::process
        Filter -->|Java Files| JavaParser[Java Parser (javalang)]:::process
    end

    %% Layer 2: Analysis Engines
    subgraph "Layer 2: Analysis Engines"
        %% Static Analysis
        PyParser --> StaticPy[Static Analyzer (Python)]:::process
        JavaParser --> StaticJava[Static Analyzer (Java)]:::process

        %% Semantic Analysis
        PyParser & JavaParser --> PreProc[Code Preprocessor]:::process
        PreProc --> LLM[LLM Embedding Model<br/>(all-MiniLM-L6-v2)]:::process
        LLM --> SemSim[Cosine Similarity Engine]:::process

        %% Dynamic Analysis
        PyParser --> Fuzzer[Dynamic Fuzzer<br/>(Python)]:::process
        JavaParser --> BCI[BCI Agent<br/>(Java Bytecode Instrumentation)]:::process
        BCI --> TraceCol[Trace Collector]:::process
    end

    %% Layer 3: Data Representation
    subgraph "Layer 3: Data Representation"
        StaticPy & StaticJava --> StructDB[(Structural Features<br/>DB)]:::storage
        SemSim --> VectorDB[(Vector Embeddings<br/>DB)]:::storage
        Fuzzer & TraceCol --> TraceDB[(Execution Logs &<br/>Anomalies)]:::storage
    end

    %% Layer 4: Intelligence & Fusion
    subgraph "Layer 4: Intelligence & Fusion"
        StructDB & VectorDB & TraceDB --> Fusion[Fusion Engine]:::process
        Fusion --> Classifier[Bug & Clone Classifier]:::process
        
        %% Logic
        Classifier -->|Score > 0.8 & Low Struct| Type4[Type-4 Clone]:::output
        Classifier -->|High Sem & Dynamic Diff| LatentBug[Latent Bug]:::output
    end

    %% Layer 5: Reporting & Visualization
    subgraph "Layer 5: Reporting"
        Classifier --> JSON[Results.json]:::output
        Classifier --> Report[Final Report]:::output
        StaticPy & StaticJava --> Viz[AST Visualizer<br/>(Mermaid Gen)]:::process
        Viz --> MMD[*.mmd Diagrams]:::output
    end
```

## Diagram Explanation

1.  **Input Processing**: The system accepts a folder containing both Python (`.py`) and Java (`.java`) files.
2.  **Analysis Engines**:
    *   **Static**: Uses `ast` for Python and `javalang` for Java to extract structural metrics (lines, branches, complexity).
    *   **Semantic**: Uses a shared LLM model to generate vector embeddings for code from both languages, enabling cross-language clone detection.
    *   **Dynamic**:
        *   **Python**: Uses a Fuzzer to run code with random inputs.
        *   **Java**: Uses a **BCI Agent** to instrument bytecode at runtime and collect execution traces.
3.  **Data Representation**: Stores features, vectors, and execution logs in intermediate databases.
4.  **Fusion Engine**: Combines the three signals (Structural, Semantic, Dynamic) using a weighted formula to classify pairs as Clones or Bugs.
5.  **Reporting**: Outputs a JSON result file, a human-readable report, and visual AST diagrams (`.mmd`).
