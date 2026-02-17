# Project Start Commands

## 1. Web UI Version (Recommended)
You need to run **two separate terminals** for the full web experience.

### Terminal 1: Backend Server
Starts the API server at `http://localhost:8000`.

```powershell
cd "c:\Users\jaswa\Downloads\q\prototype (2)\prototype"
python server.py
```

### Terminal 2: Frontend Dashboard
Starts the website at `http://localhost:3000`.

```powershell
cd "c:\Users\jaswa\Downloads\q\prototype (2)\prototype\dashboard"
npm run dev
```

---

## 2. Command Line (CMD) Version
Run the analysis directly in your terminal without the website.

### Basic Usage
```powershell
cd "c:\Users\jaswa\Downloads\q\prototype (2)\prototype"
python main.py --code_folder samples --enable_bug_detection
```

### Common Options
| Option | Description |
|--------|-------------|
| `--code_folder <path>` | Specify the folder to analyze (default: `samples`) |
| `--output_json <file>` | Save the report to a JSON file (e.g., `results.json`) |
| `--verbose` | Show detailed logs |
| `--enable_bci` | Enable Java Bytecode Instrumentation (requires `bci_injector.jar`) |
| `--file_extensions` | Filter by extensions (e.g., `.py .java .js .cpp`) |

### Example with Options
```powershell
python main.py --code_folder samples --output_json report.json --verbose
```
