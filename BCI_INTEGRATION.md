# BCI (Bytecode Instrumentation) Integration

This project now supports execution tracing for Java code using BCI (Bytecode Instrumentation) technology.

## Overview

BCI allows us to instrument Java bytecode at runtime to collect detailed execution traces, including:
- Method entry/exit events
- Class loading information
- Method call sequences
- Execution timing data

## Setup

### 1. Prerequisites

- Java JDK (Java Development Kit) installed
- Python 3.7+ with required dependencies

### 2. Download BCI Injector

Download the `bci_injector.jar` file from:
https://drive.google.com/file/d/1kqOxhM1MsdrBhIrR63YCjPfMulKpUvPX/view?usp=share_link

Place it in the project root directory as `bci_injector.jar`.

### 3. Run Setup Script

```bash
python setup_bci.py
```

This will:
- Create necessary directories
- Generate sample configuration files
- Verify Java installation
- Test BCI setup

## Usage

### Basic Usage

```bash
python main.py --code_folder samples --enable_bci
```

### Advanced Usage

```bash
python main.py --code_folder samples --semantic_threshold 0.6 --dynamic_runs 3 --enable_bci --bci_jar path/to/bci_injector.jar
```

### Parameters

- `--enable_bci`: Enable BCI execution tracing for Java files
- `--bci_jar`: Path to BCI injector jar file (default: "bci_injector.jar")
- `--code_folder`: Folder containing code to analyze
- `--semantic_threshold`: Cosine similarity threshold for semantic analysis
- `--dynamic_runs`: Number of dynamic test runs per file

## BCI Configuration

### Inclusion Filter

The inclusion filter (`bci_conf/bci_java.txt`) determines which classes/methods to instrument:

```
# Package instrumentation
package:com.example
package:org.example

# Class instrumentation
class:com.example.MyClass

# Method instrumentation
method:com.example.MyClass.myMethod
```

### BCI Agent Parameters

The BCI agent is invoked with:
```
-javaagent:<path>/bci_injector.jar=inclusion_filter_file;log_file_path;debug_logs;write_after_events
```

- `inclusion_filter_file`: Path to inclusion filter
- `log_file_path`: Path where trace data will be written
- `debug_logs`: Boolean flag for debug output
- `write_after_events`: Number of events before writing to file

## Output

### Trace Files

Execution traces are saved as CSV files in `experiments/java-traces/`:
- `trace_<timestamp>.csv`: Contains execution events
- Format: timestamp, class, method, additional_details

### Analysis Results

The pipeline provides:
- Execution event counts
- Class usage statistics
- Method call sequences
- Integration with semantic and structural analysis

## Example Output

```
[*] BCI execution tracing (Java bytecode instrumentation)...
  -> BCI traced 2 Java files
    ✓ SampleJava1.java - Trace: experiments/java-traces/trace_1234567890.csv
    ✓ SampleJava2.java - Trace: experiments/java-traces/trace_1234567891.csv

[*] BCI execution traces collected:
- SampleJava1.java: 15 events
  Trace file: experiments/java-traces/trace_1234567890.csv
  Classes: ['com.example.samples.SampleJava1', 'java.util.ArrayList']
- SampleJava2.java: 12 events
  Trace file: experiments/java-traces/trace_1234567891.csv
  Classes: ['com.example.samples.SampleJava2', 'java.util.HashMap']
```

## Troubleshooting

### Common Issues

1. **"BCI jar not found"**
   - Ensure `bci_injector.jar` is in the project root
   - Check file permissions

2. **"Java not found"**
   - Install Java JDK
   - Ensure `java` and `javac` are in PATH

3. **"Compilation failed"**
   - Check Java syntax in source files
   - Ensure all dependencies are available

4. **"Execution timed out"**
   - Java programs may run indefinitely
   - Check for infinite loops in test code

### Debug Mode

Enable debug logging by modifying the BCI agent call in `java_trace_collector.py`:
```python
result = collector.run_java_with_bci(java_file, debug_logs=True)
```

## Integration with Analysis Pipeline

BCI traces are integrated with:
- **Static Analysis**: AST parsing and structural features
- **Semantic Analysis**: Code similarity using embeddings
- **Dynamic Analysis**: Runtime behavior and anomalies
- **Fusion Scoring**: Combined scoring for clone detection

The execution traces provide additional runtime context for more accurate clone detection and code analysis.

