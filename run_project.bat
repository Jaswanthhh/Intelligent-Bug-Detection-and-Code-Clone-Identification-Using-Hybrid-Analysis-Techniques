@echo off
echo ============================================================
echo    Code Analysis Pipeline with Bug Detection
echo ============================================================
echo.
echo Installing required dependencies...
python -m pip install numpy scikit-learn sentence-transformers tqdm javalang --quiet
echo.
echo Running full analysis pipeline...
echo  - Static Analysis (AST parsing)
echo  - Semantic Analysis (embeddings)
echo  - Dynamic Testing (fuzzing)
echo  - Bug Detection (static rules, runtime, logical)
echo  - Clone Detection (fusion scoring)
echo.
echo [Scenario 1] Run with all new features (including AST Visualization for Python & Java)
python main.py --code_folder samples --semantic_threshold 0.6 --dynamic_runs 3 --show_progress --output_json results.json --verbose --file_extensions .py .java --visualize

echo.
echo [Scenario 2] Run with debug mode
python main.py --code_folder samples --debug --show_progress

echo.
echo [Scenario 3] Run with file filtering
python main.py --code_folder samples --file_extensions .py .java

echo.
echo [Scenario 4] Specific User Request
python main.py --code_folder samples --semantic_threshold 0.6 --dynamic_runs 2 --show_progress --output_json results.json --file_extensions .py --verbose

echo.
echo [Scenario 5] Scan BigCloneBench dataset (bcb_reduced)
echo NOTE: This directory has ~50k files and may take significant time to process. To run a smaller batch, you could specify a subfolder or use file extensions.
python main.py --code_folder bcb_reduced --semantic_threshold 0.6 --output_json bcb_results.json --file_extensions .java --show_progress
echo.
echo ============================================================
echo Results saved to results.json and bcb_results.json
echo ============================================================
pause
