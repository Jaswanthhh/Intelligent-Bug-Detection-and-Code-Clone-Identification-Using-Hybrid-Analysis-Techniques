@echo off
echo Running Scenario 1: All new features (Verbose, JSON output)
python main.py --code_folder samples --semantic_threshold 0.6 --dynamic_runs 3 --show_progress --output_json results.json --verbose --file_extensions .py
echo.
echo ---------------------------------------------------
echo.
echo Running Scenario 2: Debug Mode
python main.py --code_folder samples --debug --show_progress
echo.
echo ---------------------------------------------------
echo.
echo Running Scenario 3: File Filtering
python main.py --code_folder samples --file_extensions .py .java
echo.
echo ---------------------------------------------------
echo.
echo Running Scenario 4: Specific User Request
python main.py --code_folder samples --semantic_threshold 0.6 --dynamic_runs 2 --show_progress --output_json results.json --file_extensions .py --verbose
pause
