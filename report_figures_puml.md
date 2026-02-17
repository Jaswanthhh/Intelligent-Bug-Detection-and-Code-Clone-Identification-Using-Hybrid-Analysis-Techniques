# Report Figures (PlantUML)

This document contains the PlantUML code for the requested figures. You can render these using any PlantUML viewer or editor.

## Figure 1: Token-Based Clone Detection Workflow

```plantuml
@startuml
!theme plain
title Figure 1: Token-Based Clone Detection Workflow

start
:Read Source Code;
:Preprocessing;
note right
  Remove comments
  Remove whitespace
end note

:Tokenization / N-gram Generation;
note right
  Character-level N-grams
  (e.g., 3-grams)
end note

:Vectorization;
note right
  TF-IDF Transformation
  (Term Frequency-Inverse Document Frequency)
end note

:Similarity Calculation;
note right
  Cosine Similarity
  between TF-IDF vectors
end note

if (Similarity > Threshold?) then (Yes)
  :Flag as Clone;
  :Generate Report;
else (No)
  :Ignore;
endif

stop
@enduml
```

## Figure 2: AST-Based Detection Workflow

```plantuml
@startuml
!theme plain
title Figure 2: AST-Based Detection Workflow

start
:Input Source File;

if (Language?) then (Python)
  :Parse with 'ast' module;
else (Java)
  :Parse with 'javalang';
endif

:Generate Abstract Syntax Tree (AST);

partition "Feature Extraction" {
  :Count Statements;
  :Count Control Flow Branches;
  :Calculate Nesting Depth;
}

:Structural Comparison;
note right
  Compare feature vectors
  using normalized difference
end note

:Calculate Structural Score;

stop
@enduml
```

## Figure 3: Deep Learning / Semantic Detection Workflow

```plantuml
@startuml
!theme plain
title Figure 3: Deep Learning / Semantic Detection Workflow

start
:Input Code Snippet;

:Preprocessing;
note right
  Normalize text
  Truncate to model limit
end note

:LLM Encoder;
note right
  Model: all-MiniLM-L6-v2
  (Sentence-Transformers)
end note

:Generate Dense Embeddings;
note right
  384-dimensional vector
end note

:Semantic Matching;
note right
  Cosine Similarity
  Score = (A . B) / (||A|| * ||B||)
end note

if (Score > 0.75?) then (High Similarity)
  :Classify as Semantic Clone;
else (Low Similarity)
  :Classify as Distinct;
endif

stop
@enduml
```

## Figure 4: Dynamic Fuzzing Workflow

```plantuml
@startuml
!theme plain
title Figure 4: Dynamic Fuzzing Workflow

start
:Initialize Execution Engine;

repeat
  :Prepare Input / Environment;
  :Execute Code (Subprocess);
  :Capture Output Streams;
  note right
    - Stdout
    - Stderr
    - Return Code
  end note
repeat while (More Runs Needed? (Default 5))

:Analyze Execution Traces;

partition "Anomaly Detection" {
  if (Return Code != 0?) then (Yes)
    :Flag Crash/Error;
  endif
  
  if (Stderr contains Exception?) then (Yes)
    :Parse Exception Type;
    note right
      e.g., ZeroDivisionError,
      NullPointerException
    end note
  endif
}

:Generate Bug Report;

stop
@enduml
```

## Figure 5: Hybrid Fusion Model Workflow

```plantuml
@startuml
!theme plain
title Figure 5: Hybrid Fusion Model Workflow

skinparam state {
  BackgroundColor White
  BorderColor Black
}

state "Input Code Pair" as Input

state "Parallel Analysis" as Analysis {
  state "Structural Analysis\n(AST)" as Struct
  state "Semantic Analysis\n(LLM)" as Sem
  state "Dynamic Analysis\n(Fuzzing)" as Dyn
}

state "Fusion Engine" as Fusion {
  state "Weighted Summation" as Calc
  note right of Calc
    Score = (0.3 * Struct) + 
            (0.5 * Sem) + 
            (0.2 * Anomaly)
  end note
}

state "Classification" as Decision {
  state "Clone Detected" as Clone
  state "Latent Bug" as Bug
  state "No Issue" as Clean
}

Input --> Struct
Input --> Sem
Input --> Dyn

Struct --> Calc : Weight 0.3
Sem --> Calc : Weight 0.5
Dyn --> Calc : Weight 0.2

Calc --> Decision

Decision --> Clone : Score > 0.8
Decision --> Bug : High Sem + Diff Behavior
Decision --> Clean : Else
@enduml
```

## Figure 6: High-Level System Architecture

```plantuml
@startuml
!theme plain
title Figure 6: High-Level System Architecture
skinparam componentStyle uml2

package "Layer 1: Input Processing" {
    [Source Code Folder] as Src
    [File Filter] as Filter
    [Python AST Parser] as PyParser
    [Java Parser (javalang)] as JavaParser
}

package "Layer 2: Analysis Engines" {
    [Static Analyzer] as Static
    [LLM Embedding Model] as LLM
    [Dynamic Fuzzer / BCI] as Dynamic
}

package "Layer 3: Data Representation" {
    database "Structural Features" as StructDB
    database "Vector Embeddings" as VectorDB
    database "Execution Logs" as TraceDB
}

package "Layer 4: Intelligence & Fusion" {
    [Fusion Engine] as Fusion
    [Bug & Clone Classifier] as Classifier
}

package "Layer 5: Reporting" {
    [Results.json] as JSON
    [Final Report] as Report
    [Visualizations] as Viz
}

' Relationships
Src --> Filter
Filter --> PyParser
Filter --> JavaParser

PyParser --> Static
JavaParser --> Static
PyParser --> LLM
JavaParser --> LLM
PyParser --> Dynamic
JavaParser --> Dynamic

Static --> StructDB
LLM --> VectorDB
Dynamic --> TraceDB

StructDB --> Fusion
VectorDB --> Fusion
TraceDB --> Fusion

Fusion --> Classifier
Classifier --> JSON
Classifier --> Report
Classifier --> Viz

@enduml
```
