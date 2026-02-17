"""
Setup script for BCI (Bytecode Instrumentation) integration
Downloads and configures the BCI injector jar for Java execution tracing
"""
import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_bci_jar():
    """Download BCI injector jar from Google Drive"""
    bci_jar_path = "bci_injector.jar"
    
    if os.path.exists(bci_jar_path):
        print(f"BCI jar already exists at {bci_jar_path}")
        return bci_jar_path
    
    print("BCI jar not found. Please download it manually:")
    print("1. Go to: https://drive.google.com/file/d/1kqOxhM1MsdrBhIrR63YCjPfMulKpUvPX/view?usp=share_link")
    print("2. Download the bci_injector.jar file")
    print(f"3. Place it in the project root as: {bci_jar_path}")
    print("\nAlternatively, if you have the jar file, place it manually in the project root.")
    
    return None

def setup_bci_directories():
    """Create necessary directories for BCI integration"""
    directories = [
        "bci_conf",
        "experiments/java-traces",
        "bci_tracing"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_sample_configs():
    """Create sample BCI configuration files"""
    # Java inclusion filter
    java_filter = """# BCI Inclusion Filter for Java Code Analysis
# Add package names, class names, or method names to instrument
# Format: package:com.example.myapp
# Format: class:com.example.myapp.MyClass
# Format: method:com.example.myapp.MyClass.myMethod

# Example package instrumentation
package:com.example
package:org.example
package:java.util
package:java.lang

# Example class instrumentation
# class:com.example.MyClass

# Example method instrumentation
# method:com.example.MyClass.main
"""
    
    with open("bci_conf/bci_java.txt", "w") as f:
        f.write(java_filter)
    
    print("Created sample BCI configuration files")

def test_bci_setup():
    """Test if BCI setup is working"""
    bci_jar = "bci_injector.jar"
    
    if not os.path.exists(bci_jar):
        print("❌ BCI jar not found. Please download and place bci_injector.jar in project root.")
        return False
    
    # Check if Java is available
    import subprocess
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is available")
        else:
            print("❌ Java not found. Please install Java JDK.")
            return False
    except FileNotFoundError:
        print("❌ Java not found. Please install Java JDK.")
        return False
    
    # Check if javac is available
    try:
        result = subprocess.run(["javac", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java compiler (javac) is available")
        else:
            print("❌ Java compiler not found. Please install Java JDK.")
            return False
    except FileNotFoundError:
        print("❌ Java compiler not found. Please install Java JDK.")
        return False
    
    print("✅ BCI setup appears to be working")
    return True

def main():
    print("Setting up BCI (Bytecode Instrumentation) integration...")
    
    # Create directories
    setup_bci_directories()
    
    # Create sample configs
    create_sample_configs()
    
    # Check for BCI jar
    bci_jar = download_bci_jar()
    
    # Test setup
    if test_bci_setup():
        print("\n✅ BCI setup completed successfully!")
        print("\nTo use BCI tracing, run:")
        print("python main.py --code_folder samples --enable_bci")
        print("\nOr with custom BCI jar:")
        print("python main.py --code_folder samples --enable_bci --bci_jar path/to/your/bci_injector.jar")
    else:
        print("\n❌ BCI setup incomplete. Please install Java JDK and download bci_injector.jar")

if __name__ == "__main__":
    main()

