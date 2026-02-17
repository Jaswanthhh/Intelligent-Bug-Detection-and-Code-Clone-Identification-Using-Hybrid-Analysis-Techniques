"""
Demo BCI Pipeline - Simplified version for demonstration
Shows BCI integration without requiring heavy ML dependencies
"""
import os
import json
import time
from pathlib import Path
from bci_tracing.java_trace_collector import scan_java_folder_with_bci

def demo_bci_pipeline(code_folder="samples", bci_jar_path="bci_injector.jar"):
    """Demo the BCI pipeline with Java execution tracing"""
    
    print("=" * 60)
    print("BCI EXECUTION TRACE DEMONSTRATION")
    print("=" * 60)
    
    # Check if BCI jar exists
    if not os.path.exists(bci_jar_path):
        print(f"❌ BCI jar not found at {bci_jar_path}")
        print("Please download bci_injector.jar and place it in the project root")
        return
    
    # Find Java files (including subdirectories)
    java_files = list(Path(code_folder).rglob("*.java"))
    if not java_files:
        print(f"❌ No Java files found in {code_folder}")
        return
    
    print(f"📁 Found {len(java_files)} Java files:")
    for java_file in java_files:
        print(f"   - {java_file.name}")
    
    print(f"\n🔧 BCI Configuration:")
    print(f"   - JAR Path: {bci_jar_path}")
    print(f"   - Output Directory: experiments/java-traces")
    
    # Run BCI analysis
    print(f"\n🚀 Running BCI execution tracing...")
    start_time = time.time()
    
    try:
        results = scan_java_folder_with_bci(code_folder, bci_jar_path)
        
        execution_time = time.time() - start_time
        print(f"⏱️  Execution completed in {execution_time:.2f} seconds")
        
        # Display results
        print(f"\n📊 BCI Analysis Results:")
        print("=" * 40)
        
        successful_runs = 0
        total_events = 0
        
        for i, result in enumerate(results, 1):
            java_file = result.get('java_file', 'Unknown')
            success = result.get('success', False)
            trace_file = result.get('trace_file')
            error = result.get('error')
            
            print(f"\n{i}. {Path(java_file).name}")
            print(f"   Status: {'✅ Success' if success else '❌ Failed'}")
            
            if success and trace_file:
                successful_runs += 1
                trace_analysis = result.get('trace_analysis', {})
                events = trace_analysis.get('total_events', 0)
                total_events += events
                
                print(f"   📄 Trace File: {trace_file}")
                print(f"   📈 Events Captured: {events}")
                
                if trace_analysis.get('class_counts'):
                    classes = list(trace_analysis['class_counts'].keys())
                    print(f"   🏗️  Classes Instrumented: {len(classes)}")
                    for cls in classes[:3]:  # Show first 3 classes
                        print(f"      - {cls}")
                    if len(classes) > 3:
                        print(f"      ... and {len(classes) - 3} more")
                
                if trace_analysis.get('method_counts'):
                    methods = list(trace_analysis['method_counts'].keys())
                    print(f"   🔧 Methods Traced: {len(methods)}")
                    for method in methods[:3]:  # Show first 3 methods
                        print(f"      - {method}")
                    if len(methods) > 3:
                        print(f"      ... and {len(methods) - 3} more")
                        
            elif error:
                print(f"   ❌ Error: {error}")
            else:
                print(f"   ⚠️  No trace file generated")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"   - Total Java files: {len(java_files)}")
        print(f"   - Successful traces: {successful_runs}")
        print(f"   - Total events captured: {total_events}")
        print(f"   - Execution time: {execution_time:.2f}s")
        
        # Show trace file locations
        if successful_runs > 0:
            print(f"\n📁 Trace files saved to: experiments/java-traces/")
            trace_files = list(Path("experiments/java-traces").glob("*.csv"))
            if trace_files:
                print("   Generated trace files:")
                for trace_file in trace_files:
                    size = trace_file.stat().st_size
                    print(f"   - {trace_file.name} ({size} bytes)")
        
        print(f"\n✅ BCI demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ BCI analysis failed: {e}")
        import traceback
        traceback.print_exc()

def show_bci_usage():
    """Show BCI usage instructions"""
    print("\n" + "=" * 60)
    print("BCI USAGE INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Download BCI Injector JAR:")
    print("   https://drive.google.com/file/d/1kqOxhM1MsdrBhIrR63YCjPfMulKpUvPX/view?usp=share_link")
    print("   Save as: bci_injector.jar in project root")
    
    print("\n2. BCI Agent Parameters:")
    print("   -javaagent:<path>/bci_injector.jar=inclusion_filter;log_file;debug;write_after_events")
    print("   - inclusion_filter: bci_conf/bci_java.txt")
    print("   - log_file: experiments/java-traces/trace_<timestamp>.csv")
    print("   - debug: false (set to true for debug output)")
    print("   - write_after_events: 1 (write after each event)")
    
    print("\n3. Inclusion Filter Format (bci_conf/bci_java.txt):")
    print("   package:com.example          # Instrument entire package")
    print("   class:com.example.MyClass    # Instrument specific class")
    print("   method:com.example.MyClass.methodName  # Instrument specific method")
    
    print("\n4. Integration with Main Pipeline:")
    print("   python main.py --code_folder samples --enable_bci")
    print("   python main.py --code_folder samples --semantic_threshold 0.6 --enable_bci")

if __name__ == "__main__":
    print("BCI (Bytecode Instrumentation) Integration Demo")
    print("This demonstrates execution tracing for Java code using BCI")
    
    # Show usage instructions
    show_bci_usage()
    
    # Run demo
    demo_bci_pipeline()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Download the real bci_injector.jar from the Google Drive link")
    print(f"2. Replace the mock jar file with the real one")
    print(f"3. Run: python main.py --code_folder samples --enable_bci")
    print(f"4. Check experiments/java-traces/ for execution trace files")
