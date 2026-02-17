"""
Top-level CLI to run the prototype pipeline:
1. Static analysis (AST)
2. Semantic analysis (embeddings)
3. Dynamic testing (randomized runs)
4. BCI execution tracing (Java bytecode instrumentation)
5. Bug detection (static rules, runtime analysis, logical checking)
6. Fusion scoring & reporting

Usage:
    python main.py --code_folder path/to/code --semantic_threshold 0.75 --enable_bci
"""
import argparse, json, time, os, logging
from static_analysis.ast_parser import scan_code_folder
from static_analysis.ast_parser import scan_code_folder
try:
    from semantic_analysis.llm_embeddings import find_similar_pairs
except ImportError:
    print("[!] Warning: sentence-transformers not found or failed to import. Semantic analysis will be disabled.")
    find_similar_pairs = lambda *args, **kwargs: []
except AttributeError:
    print("[!] Warning: sentence-transformers import error. Semantic analysis will be disabled.")
    find_similar_pairs = lambda *args, **kwargs: []

from dynamic_testing.rl_tester import scan_folder_dynamic
from dynamic_testing.rl_tester import scan_folder_dynamic
from classifier.fusion_model import build_snippet_records, structural_similarity, fusion_score
from bci_tracing.java_trace_collector import scan_java_folder_with_bci
from bug_detection.detector import detect_bugs
from visualization.ast_visualizer import generate_ast_diagram

def setup_logging(verbose=False, debug=False):
    """Setup logging based on verbosity level"""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)

def run_pipeline(paths, semantic_threshold=0.75, dynamic_runs=5, enable_bci=False, bci_jar_path="bci_injector.jar", show_progress=False, file_extensions=None, verbose=False, debug=False, enable_bug_detection=True, enable_visualization=False):
    logger = setup_logging(verbose=verbose, debug=debug)
    
    if debug:
        logger.debug(f"Starting pipeline with parameters: paths={paths}, threshold={semantic_threshold}, dynamic_runs={dynamic_runs}")
    
    if file_extensions:
        print(f"[*] Filtering files by extensions: {file_extensions}")
        logger.info(f"File extension filter: {file_extensions}")
    print("[*] Static analysis...")
    logger.debug("Beginning static analysis phase")
    static_results = scan_code_folder(paths, show_progress=show_progress, file_extensions=file_extensions)
    print(f"  -> scanned {len(static_results)} files")
    logger.info(f"Static analysis completed: {len(static_results)} files scanned")
    if debug:
        logger.debug(f"Static results: {[r.get('path', 'unknown') for r in static_results[:5]]}")

    print("[*] Build snippet records...")
    logger.debug("Building snippet records from static analysis")
    snippet_records = build_snippet_records(static_results)
    print(f"  -> extracted {len(snippet_records)} function/method snippets")
    logger.info(f"Extracted {len(snippet_records)} snippets")
    if debug:
        logger.debug(f"Sample snippets: {[s.get('func_name', 'unknown') for s in snippet_records[:5]]}")

    print("[*] Semantic analysis (embedding similarities)...")
    logger.debug("Beginning semantic analysis with embeddings")
    sem_pairs = find_similar_pairs(snippet_records, threshold=semantic_threshold, show_progress=show_progress)
    print(f"  -> found {len(sem_pairs)} semantic-similar pairs (threshold={semantic_threshold})")
    logger.info(f"Semantic analysis found {len(sem_pairs)} similar pairs")
    if debug and sem_pairs:
        logger.debug(f"Top semantic pair: {sem_pairs[0].get('a', {}).get('func_name')} <-> {sem_pairs[0].get('b', {}).get('func_name')} (score={sem_pairs[0].get('score', 0):.3f})")

    print("[*] Dynamic testing (simple fuzzing)...")
    logger.debug("Beginning dynamic testing phase")
    # dyn_results = scan_folder_dynamic(code_folder, runs_per_file=dynamic_runs, show_progress=show_progress, file_extensions=file_extensions)
    # Update to handle list of paths
    dyn_results = []
    for p in paths:
        if os.path.isdir(p):
            dyn_results.extend(scan_folder_dynamic(p, runs_per_file=dynamic_runs, show_progress=show_progress, file_extensions=file_extensions))
        elif os.path.isfile(p):
            # scan_folder_dynamic might expect a folder, but let's see. 
            # If it expects folder, we might need to handle file case.
            # For now, let's assume it handles folders. 
            # Actually, to be safe, let's update rl_tester.py to handle list of paths.
            # But I can't see rl_tester.py right now.
            # Let's just pass the list and update rl_tester.py to accept it.
            pass 
    
    # Better approach: Update scan_folder_dynamic to accept list of paths
    from dynamic_testing.rl_tester import scan_paths_dynamic
    dyn_results = scan_paths_dynamic(paths, runs_per_file=dynamic_runs, show_progress=show_progress, file_extensions=file_extensions)
    # Redundant code block removed

    anomaly_map = {}
    for r in dyn_results:
        path = r.get("path")
        anomalies = r.get("anomalies", [])
        if anomalies:
            anomaly_map[path] = anomalies
            logger.debug(f"Anomalies found in {path}: {len(anomalies)}")
    logger.info(f"Dynamic testing completed: {len(dyn_results)} files tested, {len(anomaly_map)} with anomalies")

    # BCI execution tracing for Java files
    bci_results = []
    if enable_bci and os.path.exists(bci_jar_path):
        print("[*] BCI execution tracing (Java bytecode instrumentation)...")
        logger.debug(f"BCI tracing enabled, jar path: {bci_jar_path}")
        try:
            from bci_tracing.java_trace_collector import scan_paths_with_bci
            bci_results = scan_paths_with_bci(paths, bci_jar_path)
            print(f"  -> BCI traced {len(bci_results)} Java files")
            logger.info(f"BCI tracing completed: {len(bci_results)} files")
            
            # Display BCI results summary
            for result in bci_results:
                if result.get("success"):
                    print(f"    ✓ {os.path.basename(result['java_file'])} - Trace: {result.get('trace_file', 'N/A')}")
                    logger.debug(f"BCI success: {result['java_file']}")
                else:
                    print(f"    ✗ {os.path.basename(result['java_file'])} - Error: {result.get('error', 'Unknown')}")
                    logger.warning(f"BCI failed for {result.get('java_file', 'unknown')}: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"  -> BCI tracing failed: {e}")
            logger.error(f"BCI tracing exception: {e}", exc_info=debug)
    elif enable_bci:
        print(f"[*] BCI tracing skipped - BCI jar not found at {bci_jar_path}")
        logger.warning(f"BCI jar not found at {bci_jar_path}")
    else:
        print("[*] BCI tracing disabled")
        logger.debug("BCI tracing disabled")

    # Bug Detection
    bug_results = []
    bug_stats = {}
    bug_summary = ""
    if enable_bug_detection:
        print("\n[*] Bug Detection...")
        logger.debug("Beginning bug detection phase")
        try:
            bug_results, bug_stats, bug_summary = detect_bugs(
                static_results, 
                dyn_results, 
                snippet_records,
                show_progress=show_progress
            )
            print(f"  -> Found {len(bug_results)} potential bugs")
            logger.info(f"Bug detection completed: {len(bug_results)} bugs found")
            
            # Display critical bugs immediately
            critical_bugs = [b for b in bug_results if b.get("severity") in ("critical", "high")]
            if critical_bugs:
                print(f"\n  [!] {len(critical_bugs)} CRITICAL/HIGH severity bugs detected!")
                for bug in critical_bugs[:5]:  # Show top 5
                    print(f"    [{bug.get('severity', '').upper()}] {bug.get('file', 'unknown')}:{bug.get('line', 0)}")
                    print(f"      {bug.get('message', '')}")
                if len(critical_bugs) > 5:
                    print(f"    ... and {len(critical_bugs) - 5} more critical/high bugs")
        except Exception as e:
            print(f"  -> Bug detection failed: {e}")
            logger.error(f"Bug detection exception: {e}", exc_info=debug)
    else:
        print("[*] Bug detection disabled")

    # Visualization
    if enable_visualization:
        print("\n[*] Generating AST Execution Diagrams...")
        logger.debug("Beginning visualization phase")
        count = 0
        for result in static_results:
            path = result.get("path")
            if path and path.endswith(".py"):
                try:
                    out = generate_ast_diagram(path)
                    if out:
                        count += 1
                        if verbose:
                            print(f"  -> Generated diagram: {out}")
                except Exception as e:
                    logger.error(f"Failed to visualize {path}: {e}")
            elif path and path.endswith(".java"):
                try:
                    from visualization.ast_visualizer import generate_java_ast_diagram
                    out = generate_java_ast_diagram(path, bci_jar_path)
                    if out:
                        count += 1
                        if verbose:
                            print(f"  -> Generated diagram: {out}")
                except Exception as e:
                    logger.error(f"Failed to visualize {path}: {e}")
        print(f"  -> Generated {count} AST diagrams")

    # Fusion: combine for the top semantic pairs
    print("[*] Fusion & scoring...")
    logger.debug("Beginning fusion scoring phase")
    reports = []
    
    if show_progress:
        try:
            from tqdm import tqdm
            pair_iter = tqdm(sem_pairs, desc="Computing fusion scores", unit="pair")
        except ImportError:
            pair_iter = sem_pairs
    else:
        pair_iter = sem_pairs
    
    # Import new detailed fusion function
    from classifier.fusion_model import fusion_score_detailed
    
    for p in pair_iter:
        logger.debug(f"Processing pair: {p.get('a', {}).get('func_name')} <-> {p.get('b', {}).get('func_name')}")
        a = p['a']; b = p['b']; sem_score = p['score']
        struct_sim = structural_similarity(a.get('features', {}), b.get('features', {}))
        dyn_a = bool(anomaly_map.get(a.get('file')))
        dyn_b = bool(anomaly_map.get(b.get('file')))
        dyn_flag = dyn_a or dyn_b
        
        # Use new detailed scoring
        total_score, components, explanation = fusion_score_detailed(struct_sim, sem_score, dyn_flag)
        
        reports.append({
            "file_a": a.get('file'), "func_a": a.get('func_name'),
            "file_b": b.get('file'), "func_b": b.get('func_name'),
            "struct_sim": struct_sim, "semantic_sim": sem_score,
            "dynamic_anomaly": dyn_flag, 
            "fusion_score": total_score,
            "score_components": components, # XAI: Breakdown
            "explanation": explanation      # XAI: Human-readable reason
        })
    # sort by fusion_score descending
    reports.sort(key=lambda x: -x["fusion_score"])
    logger.info(f"Fusion scoring completed: {len(reports)} reports generated")
    if debug and reports:
        logger.debug(f"Top fusion score: {reports[0].get('fusion_score', 0):.3f}")
    
    # Bug Propagation Logic
    print("[*] Analyzing Bug Propagation...")
    from bug_detection.detector import propagate_bugs_by_clones
    propagated_bugs = propagate_bugs_by_clones(bug_results, reports)
    if propagated_bugs:
        print(f"  -> Found {len(propagated_bugs)} latent bugs via clone propagation")
        bug_results.extend(propagated_bugs)
        # Re-sort bugs
        bug_results.sort(key=lambda b: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(b.get("severity", "info"), 99)
        ))
    
    print("[*] Results (top candidates):")
    for r in reports[:20]:
        print(json.dumps(r, indent=2))

    # Print dynamic anomalies summary
    if anomaly_map:
        print("\n[*] Dynamic anomalies found in the following files:")
        for path, anomalies in anomaly_map.items():
            print(f"- {path}: {len(anomalies)} anomalous runs (sample):")
            print(json.dumps(anomalies[:2], indent=2))
    else:
        print("\n[*] No dynamic anomalies detected (in prototype runs).")

    # Print BCI execution traces summary
    if bci_results:
        print("\n[*] BCI execution traces collected:")
        for result in bci_results:
            if result.get("success") and result.get("trace_file"):
                trace_analysis = result.get("trace_analysis", {})
                if not trace_analysis.get("error"):
                    print(f"- {os.path.basename(result['java_file'])}: {trace_analysis.get('total_events', 0)} events")
                    print(f"  Trace file: {result['trace_file']}")
                    if trace_analysis.get("class_counts"):
                        print(f"  Classes: {list(trace_analysis['class_counts'].keys())}")
                else:
                    print(f"- {os.path.basename(result['java_file'])}: Trace analysis failed - {trace_analysis.get('error')}")

    # Calculate and display summary statistics
    print("\n" + "="*60)
    print("[*] SUMMARY STATISTICS")
    print("="*60)
    
    # Basic counts
    total_files = len(static_results)
    total_snippets = len(snippet_records)
    total_clone_pairs = len(sem_pairs)
    total_reports = len(reports)
    files_with_anomalies = len(anomaly_map)
    total_anomalies = sum(len(anoms) for anoms in anomaly_map.values())
    
    print(f"Files Analyzed: {total_files}")
    print(f"Code Snippets Extracted: {total_snippets}")
    print(f"Clone Pairs Detected: {total_clone_pairs}")
    print(f"Fusion Reports Generated: {total_reports}")
    print(f"Files with Dynamic Anomalies: {files_with_anomalies}")
    print(f"Total Dynamic Anomalies: {total_anomalies}")
    
    # Similarity statistics
    if sem_pairs:
        similarities = [p.get('score', 0) for p in sem_pairs]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        max_similarity = max(similarities) if similarities else 0
        min_similarity = min(similarities) if similarities else 0
        print(f"\nSemantic Similarity Statistics:")
        print(f"  Average: {avg_similarity:.3f}")
        print(f"  Maximum: {max_similarity:.3f}")
        print(f"  Minimum: {min_similarity:.3f}")
        print(f"  Median: {sorted(similarities)[len(similarities)//2]:.3f}")
    
    # Fusion score statistics
    if reports:
        fusion_scores = [r.get('fusion_score', 0) for r in reports]
        avg_fusion = sum(fusion_scores) / len(fusion_scores) if fusion_scores else 0
        max_fusion = max(fusion_scores) if fusion_scores else 0
        min_fusion = min(fusion_scores) if fusion_scores else 0
        high_confidence = sum(1 for s in fusion_scores if s >= 0.7)
        print(f"\nFusion Score Statistics:")
        print(f"  Average: {avg_fusion:.3f}")
        print(f"  Maximum: {max_fusion:.3f}")
        print(f"  Minimum: {min_fusion:.3f}")
        print(f"  High Confidence (>=0.7): {high_confidence} ({100*high_confidence/len(reports):.1f}%)")
    
    # Structural similarity statistics
    if reports:
        struct_sims = [r.get('struct_sim', 0) for r in reports]
        avg_struct = sum(struct_sims) / len(struct_sims) if struct_sims else 0
        print(f"\nStructural Similarity Statistics:")
        print(f"  Average: {avg_struct:.3f}")
    
    # Dynamic anomaly statistics
    if dyn_results:
        total_runs = sum(r.get('runs', 0) for r in dyn_results)
        anomaly_rate = (total_anomalies / total_runs * 100) if total_runs > 0 else 0
        print(f"\nDynamic Testing Statistics:")
        print(f"  Total Test Runs: {total_runs}")
        print(f"  Anomaly Rate: {anomaly_rate:.2f}%")
    
    # BCI statistics
    if bci_results:
        successful_traces = sum(1 for r in bci_results if r.get('success'))
        total_events = sum(r.get('trace_analysis', {}).get('total_events', 0) for r in bci_results if r.get('success'))
        print(f"\nBCI Tracing Statistics:")
        print(f"  Successful Traces: {successful_traces}/{len(bci_results)}")
        print(f"  Total Events Captured: {total_events}")
    
    # File type breakdown
    if static_results:
        file_types = {}
        for r in static_results:
            path = r.get('path', '')
            ext = os.path.splitext(path)[1] or 'no_ext'
            file_types[ext] = file_types.get(ext, 0) + 1
        if file_types:
            print(f"\nFile Type Breakdown:")
            for ext, count in sorted(file_types.items(), key=lambda x: -x[1]):
                print(f"  {ext or '(no extension)'}: {count} files")
    
    # Bug detection statistics
    if bug_results:
        print(f"\nBug Detection Statistics:")
        print(f"  Total Bugs Found: {len(bug_results)}")
        if bug_stats:
            severity_counts = bug_stats.get("by_severity", {})
            for sev in ["critical", "high", "medium", "low", "info"]:
                count = severity_counts.get(sev, 0)
                if count > 0:
                    marker = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]", "low": "[.]", "info": "[i]"}.get(sev, "")
                    print(f"    {marker} {sev.upper()}: {count}")
            
            # Top bug categories
            category_counts = bug_stats.get("by_category", {})
            if category_counts:
                print(f"  Top Bug Categories:")
                sorted_cats = sorted(category_counts.items(), key=lambda x: -x[1])[:5]
                for cat, count in sorted_cats:
                    print(f"    - {cat}: {count}")
    
    print("="*60)
    
    # Print detailed bug report
    if bug_results:
        print("\n" + "="*60)
        print("[*] DETAILED BUG REPORT")
        print("="*60)
        
        # Group bugs by file
        bugs_by_file = {}
        for bug in bug_results:
            filepath = bug.get("file", "unknown")
            if filepath not in bugs_by_file:
                bugs_by_file[filepath] = []
            bugs_by_file[filepath].append(bug)
        
        for filepath, file_bugs in bugs_by_file.items():
            print(f"\n[FILE] {filepath} ({len(file_bugs)} bugs)")
            for bug in sorted(file_bugs, key=lambda b: b.get("line", 0)):
                sev = bug.get("severity", "unknown")
                marker = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]", "low": "[.]", "info": "[i]"}.get(sev, "[ ]")
                line = bug.get("line", 0)
                func = bug.get("function", "")
                func_str = f" in {func}()" if func else ""
                print(f"  {marker} Line {line}{func_str}: [{sev.upper()}] {bug.get('category', '')}")
                print(f"      {bug.get('message', '')}")
                if bug.get('evidence'):
                    evidence = bug.get('evidence', '')[:100]
                    print(f"      Evidence: {evidence}")
        
        print("="*60)

    return {"static": static_results, "semantic_pairs": sem_pairs, "dynamic": dyn_results, "bci": bci_results, "reports": reports, "bugs": bug_results, "bug_stats": bug_stats}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code_folder", type=str, default="samples", help="Folder with code to analyze")
    parser.add_argument("--semantic_threshold", type=float, default=0.75, help="Cosine similarity threshold for semantic pairing")
    parser.add_argument("--dynamic_runs", type=int, default=5, help="Number of randomized dynamic runs per file")
    parser.add_argument("--enable_bci", action="store_true", help="Enable BCI execution tracing for Java files")
    parser.add_argument("--bci_jar", type=str, default="bci_injector.jar", help="Path to BCI injector jar file")
    parser.add_argument("--show_progress", action="store_true", help="Show progress bars for long-running operations")
    parser.add_argument("--output_json", type=str, default=None, help="Save results to JSON file (e.g., results.json)")
    parser.add_argument("--file_extensions", type=str, nargs="+", default=None, help="Filter files by extension (e.g., --file_extensions .py .java)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging (INFO level)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging (DEBUG level, most verbose)")
    parser.add_argument("--enable_bug_detection", action="store_true", default=True, help="Enable bug detection (default: enabled)")
    parser.add_argument("--disable_bug_detection", action="store_true", help="Disable bug detection")
    parser.add_argument("--visualize", action="store_true", help="Generate AST execution diagrams for Python files")
    parser.add_argument("--evolution", action="store_true", help="Enable git evolution analysis")
    args = parser.parse_args()
    
    # Handle bug detection flag
    enable_bugs = args.enable_bug_detection and not args.disable_bug_detection
    
    start = time.time()
    # CLI passes a single folder string, wrap it in list
    paths = [args.code_folder]
    results = run_pipeline(paths, semantic_threshold=args.semantic_threshold, dynamic_runs=args.dynamic_runs, enable_bci=args.enable_bci, bci_jar_path=args.bci_jar, show_progress=args.show_progress, file_extensions=args.file_extensions, verbose=args.verbose, debug=args.debug, enable_bug_detection=enable_bugs, enable_visualization=args.visualize)
    
    # Save to JSON if requested
    if args.output_json:
        # Prepare JSON-serializable results
        json_output = {
            "metadata": {
                "code_folder": args.code_folder,
                "semantic_threshold": args.semantic_threshold,
                "dynamic_runs": args.dynamic_runs,
                "enable_bci": args.enable_bci,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "execution_time_seconds": round(time.time() - start, 2)
            },
            "static_analysis": {
                "total_files": len(results["static"]),
                "files": results["static"]
            },
            "semantic_analysis": {
                "total_pairs": len(results["semantic_pairs"]),
                "pairs": results["semantic_pairs"]
            },
            "dynamic_testing": {
                "total_files_tested": len(results["dynamic"]),
                "results": results["dynamic"]
            },
            "bci_tracing": {
                "total_files_traced": len(results["bci"]),
                "results": results["bci"]
            },
            "fusion_reports": {
                "total_reports": len(results["reports"]),
                "reports": results["reports"]
            },
            "summary_statistics": {
                "total_files": len(results["static"]),
                "total_snippets": len(build_snippet_records(results["static"])),
                "total_clone_pairs": len(results["semantic_pairs"]),
                "total_reports": len(results["reports"]),
                "files_with_anomalies": len([r for r in results["dynamic"] if r.get("anomalies")]),
                "total_anomalies": sum(len(r.get("anomalies", [])) for r in results["dynamic"]),
                "average_similarity": sum(p.get("score", 0) for p in results["semantic_pairs"]) / len(results["semantic_pairs"]) if results["semantic_pairs"] else 0,
                "average_fusion_score": sum(r.get("fusion_score", 0) for r in results["reports"]) / len(results["reports"]) if results["reports"] else 0
            },
            "bug_detection": {
                "total_bugs": len(results.get("bugs", [])),
                "stats": results.get("bug_stats", {}),
                "bugs": results.get("bugs", [])
            }
        }
        
        # Git Evolution Analysis
        if args.evolution:
            try:
                from git_evolution import GitEvolutionAnalyzer
                print("[*] Running Git Evolution Analysis...")
                
                # Check if current dir or parent is repo
                repo_path = "."
                try:
                    analyzer = GitEvolutionAnalyzer(repo_path)
                except:
                    repo_path = ".."
                    analyzer = GitEvolutionAnalyzer(repo_path)
                    
                print(f"    - Using git repo at: {os.path.abspath(repo_path)}")
                commits = analyzer.get_commit_history(limit=5)
                evolution_data = analyzer.analyze_evolution(commits, args.file_extensions)
                json_output["evolution"] = evolution_data
                print(f"    - Analyzed {len(evolution_data)} commits")
            except Exception as e:
                print(f"[!] Git Evolution Analysis failed: {e}")
                json_output["evolution"] = {"error": str(e)}

        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        print(f"\n[*] Results saved to {args.output_json}")
    
    print(f"\nDone in {time.time()-start:.2f}s")
