"""
Test script for BCI integration
Tests the BCI functionality without requiring all pipeline dependencies
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_bci_module_import():
    """Test if BCI module can be imported"""
    try:
        from bci_tracing.java_trace_collector import JavaTraceCollector, scan_java_folder_with_bci
        print("✅ BCI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import BCI module: {e}")
        return False

def test_java_files_exist():
    """Test if sample Java files exist"""
    java_files = list(Path("samples").glob("*.java"))
    if java_files:
        print(f"✅ Found {len(java_files)} Java files: {[f.name for f in java_files]}")
        return True
    else:
        print("❌ No Java files found in samples directory")
        return False

def test_bci_config_files():
    """Test if BCI configuration files exist"""
    config_files = [
        "bci_conf/bci_java.txt",
        "bci_conf/bci_python.txt"
    ]
    
    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ Configuration file exists: {config_file}")
        else:
            print(f"❌ Configuration file missing: {config_file}")
            all_exist = False
    
    return all_exist

def test_bci_jar():
    """Test if BCI jar file exists"""
    bci_jar = "bci_injector.jar"
    if os.path.exists(bci_jar):
        print(f"✅ BCI jar file exists: {bci_jar}")
        return True
    else:
        print(f"❌ BCI jar file missing: {bci_jar}")
        return False

def test_java_compilation():
    """Test if Java files can be compiled"""
    java_files = list(Path("samples").glob("*.java"))
    if not java_files:
        print("❌ No Java files to test compilation")
        return False
    
    import subprocess
    try:
        # Test compilation of first Java file
        java_file = java_files[0]
        result = subprocess.run(
            ["javac", str(java_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Java compilation successful: {java_file.name}")
            return True
        else:
            print(f"❌ Java compilation failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Java compiler (javac) not found")
        return False

def test_bci_collector_creation():
    """Test if BCI collector can be created"""
    try:
        from bci_tracing.java_trace_collector import JavaTraceCollector
        collector = JavaTraceCollector("bci_injector.jar")
        print("✅ BCI collector created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create BCI collector: {e}")
        return False

def main():
    print("Testing BCI Integration...")
    print("=" * 50)
    
    tests = [
        ("BCI Module Import", test_bci_module_import),
        ("Java Files Exist", test_java_files_exist),
        ("BCI Config Files", test_bci_config_files),
        ("BCI JAR File", test_bci_jar),
        ("Java Compilation", test_java_compilation),
        ("BCI Collector Creation", test_bci_collector_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  Test failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! BCI integration is ready.")
        print("\nTo run the full pipeline with BCI:")
        print("python main.py --code_folder samples --enable_bci")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        
        if not os.path.exists("bci_injector.jar"):
            print("\nTo complete setup:")
            print("1. Download bci_injector.jar from the Google Drive link")
            print("2. Place it in the project root directory")
            print("3. Run this test again")

if __name__ == "__main__":
    main()
