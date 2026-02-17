"""
IBD LSP Server — Real-time bug detection & clone highlighting for VS Code.

Uses pygls to implement a Language Server Protocol server that:
1. Runs static analysis (AST-based bug detection) on every file change
2. Detects code clones via Jaccard similarity across workspace files
3. Sends diagnostics + custom clone notifications to the VS Code extension
"""

import sys
import os
import re
import ast
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

# Add prototype root to path so we can import our analysis modules
_PROTO_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROTO_ROOT not in sys.path:
    sys.path.insert(0, _PROTO_ROOT)

# pygls v2 imports
from pygls.lsp.server import LanguageServer
from lsprotocol import types

# ────────────────────────────────────────────────────────────────
# Logging
# ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
log = logging.getLogger("ibd-lsp")

# ────────────────────────────────────────────────────────────────
# Our analysis modules (imported from project)
# ────────────────────────────────────────────────────────────────
from bug_detection.static_rules import (
    StaticBugDetector,
    JavaStaticBugDetector,
    JSStaticBugDetector,
    CppStaticBugDetector,
)

try:
    from static_analysis.ast_parser import extract_python_functions
except ImportError:
    extract_python_functions = None

# ────────────────────────────────────────────────────────────────
# Clone Detection (lightweight Jaccard, no ML model)
# ────────────────────────────────────────────────────────────────

def _tokenize(code: str) -> Set[str]:
    """Split code into token set for Jaccard similarity."""
    tokens = set(re.split(r"\W+", code.lower()))
    tokens.discard("")
    return tokens


def jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two code snippets."""
    set_a = _tokenize(a)
    set_b = _tokenize(b)
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def find_clones_in_functions(
    functions: List[Dict[str, Any]], threshold: float = 0.75
) -> List[Dict[str, Any]]:
    """
    Compare all function pairs and return those above the similarity threshold.
    Each function dict must have: file, name, start, end, code.
    """
    clones = []
    n = len(functions)
    for i in range(n):
        code_a = functions[i].get("code", "")
        if not code_a or len(code_a.strip()) < 20:
            continue
        for j in range(i + 1, n):
            code_b = functions[j].get("code", "")
            if not code_b or len(code_b.strip()) < 20:
                continue
            score = jaccard_similarity(code_a, code_b)
            if score >= threshold:
                clones.append(
                    {
                        "a": {
                            "file": functions[i]["file"],
                            "name": functions[i]["name"],
                            "start": functions[i]["start"],
                            "end": functions[i]["end"],
                        },
                        "b": {
                            "file": functions[j]["file"],
                            "name": functions[j]["name"],
                            "start": functions[j]["start"],
                            "end": functions[j]["end"],
                        },
                        "score": round(score, 4),
                    }
                )
    clones.sort(key=lambda x: -x["score"])
    return clones


# ────────────────────────────────────────────────────────────────
# Language Server
# ────────────────────────────────────────────────────────────────

server = LanguageServer("ibd-lsp", "v1.0.0")

# In-memory workspace function registry for clone detection
_workspace_functions: Dict[str, List[Dict[str, Any]]] = {}

# Debounce timers
_debounce_tasks: Dict[str, asyncio.Task] = {}

# Config defaults
_config = {
    "enable_real_time": True,
    "clone_threshold": 0.75,
    "debounce_ms": 500,
}

# Bug detectors (reusable instances)
_py_detector = StaticBugDetector()
_java_detector = JavaStaticBugDetector()
_js_detector = JSStaticBugDetector()
_cpp_detector = CppStaticBugDetector()


def _severity_to_lsp(severity: str) -> types.DiagnosticSeverity:
    """Map our severity strings to LSP DiagnosticSeverity."""
    mapping = {
        "critical": types.DiagnosticSeverity.Error,
        "high": types.DiagnosticSeverity.Warning,
        "medium": types.DiagnosticSeverity.Warning,
        "low": types.DiagnosticSeverity.Information,
        "info": types.DiagnosticSeverity.Hint,
    }
    return mapping.get(severity, types.DiagnosticSeverity.Information)


def _get_detector(uri: str):
    """Pick the right detector based on file extension."""
    lower = uri.lower()
    if lower.endswith(".py"):
        return _py_detector
    elif lower.endswith(".java"):
        return _java_detector
    elif lower.endswith((".js", ".jsx", ".ts", ".tsx")):
        return _js_detector
    elif lower.endswith((".cpp", ".c", ".h", ".hpp")):
        return _cpp_detector
    return None


def _extract_functions_from_source(uri: str, source: str) -> List[Dict[str, Any]]:
    """Extract function info from source code for clone detection."""
    functions = []
    lower = uri.lower()

    if lower.endswith(".py") and extract_python_functions is not None:
        try:
            funcs = extract_python_functions(source)
            for f in funcs:
                functions.append(
                    {
                        "file": uri,
                        "name": f.get("name", "<unknown>"),
                        "start": f.get("start", 0),
                        "end": f.get("end", 0),
                        "code": f.get("code", ""),
                    }
                )
        except Exception as e:
            log.debug(f"Function extraction failed for {uri}: {e}")

    return functions


def _run_analysis(uri: str, source: str) -> List[types.Diagnostic]:
    """Run bug detection and return LSP diagnostics."""
    detector = _get_detector(uri)
    if detector is None:
        return []

    # Determine a filepath-like string for the detector
    filepath = uri
    if filepath.startswith("file:///"):
        filepath = filepath[8:]  # strip file:/// prefix
    elif filepath.startswith("file://"):
        filepath = filepath[7:]

    try:
        bugs = detector.detect_bugs_in_code(source, filepath)
    except Exception as e:
        log.error(f"Bug detection error for {uri}: {e}")
        return []

    diagnostics: List[types.Diagnostic] = []
    for bug in bugs:
        line = max(0, (bug.get("line", 1) or 1) - 1)
        sev = _severity_to_lsp(bug.get("severity", "info"))
        msg = bug.get("message", "Unknown issue")
        category = bug.get("category", "")
        evidence = bug.get("evidence", "")
        suggestion = bug.get("suggestion", "")

        detail_parts = []
        if category:
            detail_parts.append(f"[{category}]")
        if evidence:
            detail_parts.append(evidence)
        if suggestion:
            detail_parts.append(f"Fix: {suggestion}")
        detail = " — ".join(detail_parts)

        diag = types.Diagnostic(
            range=types.Range(
                start=types.Position(line=line, character=0),
                end=types.Position(line=line, character=999),
            ),
            message=f"{msg}\n{detail}" if detail else msg,
            severity=sev,
            source="IBD",
            code=category or None,
        )
        diagnostics.append(diag)

    return diagnostics


async def _analyze_and_publish(uri: str, source: str):
    """Run analysis, publish diagnostics, and detect clones."""
    if not _config["enable_real_time"]:
        return

    # 1) Static bug detection → diagnostics
    diagnostics = _run_analysis(uri, source)
    server.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=uri,
            diagnostics=diagnostics,
        )
    )
    log.info(f"Published {len(diagnostics)} diagnostics for {uri}")

    # 2) Extract functions for clone detection
    functions = _extract_functions_from_source(uri, source)
    _workspace_functions[uri] = functions

    # 3) Gather all functions across workspace
    all_functions: List[Dict[str, Any]] = []
    for funcs in _workspace_functions.values():
        all_functions.extend(funcs)

    if len(all_functions) >= 2:
        clones = find_clones_in_functions(
            all_functions, threshold=_config["clone_threshold"]
        )
        if clones:
            log.info(f"Found {len(clones)} clone pairs in workspace")
        # Send custom notification to extension
        server.send_notification("ibd/cloneResults", {"clones": clones, "uri": uri})


async def _debounced_analyze(uri: str, source: str, delay_ms: int):
    """Wait for debounce period, then run analysis."""
    await asyncio.sleep(delay_ms / 1000.0)
    await _analyze_and_publish(uri, source)


def _schedule_analysis(uri: str, source: str):
    """Schedule a debounced analysis for the given document."""
    # Cancel existing timer for this URI
    existing = _debounce_tasks.get(uri)
    if existing and not existing.done():
        existing.cancel()

    loop = asyncio.get_event_loop()
    task = loop.create_task(
        _debounced_analyze(uri, source, _config["debounce_ms"])
    )
    _debounce_tasks[uri] = task


# ────────────────────────────────────────────────────────────────
# LSP Lifecycle Handlers
# ────────────────────────────────────────────────────────────────

@server.feature(types.INITIALIZE)
def on_initialize(params: types.InitializeParams):
    log.info("IBD LSP Server initializing...")

    # Read config from initializationOptions if provided
    opts = params.initialization_options or {}
    if isinstance(opts, dict):
        if "enableRealTimeAnalysis" in opts:
            _config["enable_real_time"] = bool(opts["enableRealTimeAnalysis"])
        if "cloneThreshold" in opts:
            _config["clone_threshold"] = float(opts["cloneThreshold"])
        if "debounceMs" in opts:
            _config["debounce_ms"] = int(opts["debounceMs"])

    log.info(f"Config: {_config}")

    return types.InitializeResult(
        capabilities=types.ServerCapabilities(
            text_document_sync=types.TextDocumentSyncOptions(
                open_close=True,
                change=types.TextDocumentSyncKind.Full,
                save=types.SaveOptions(include_text=True),
            ),
            code_lens_provider=types.CodeLensOptions(resolve_provider=False),
        ),
        server_info=types.ServerInfo(name="ibd-lsp", version="1.0.0"),
    )


@server.feature(types.INITIALIZED)
def on_initialized(params: types.InitializedParams):
    log.info("IBD LSP Server initialized and ready!")


@server.feature(types.SHUTDOWN)
def on_shutdown(params):
    log.info("IBD LSP Server shutting down...")
    # Cancel all pending tasks
    for task in _debounce_tasks.values():
        if not task.done():
            task.cancel()
    return None


# ────────────────────────────────────────────────────────────────
# Document Sync Handlers
# ────────────────────────────────────────────────────────────────

@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def on_did_open(params: types.DidOpenTextDocumentParams):
    """Analyze immediately when a document is opened."""
    uri = params.text_document.uri
    source = params.text_document.text
    log.info(f"Document opened: {uri}")
    _schedule_analysis(uri, source)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def on_did_change(params: types.DidChangeTextDocumentParams):
    """Re-analyze on every change (debounced)."""
    uri = params.text_document.uri
    # With Full sync, last content change has the full text
    if params.content_changes:
        source = params.content_changes[-1].text
        _schedule_analysis(uri, source)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def on_did_save(params: types.DidSaveTextDocumentParams):
    """Re-analyze on save (also triggers clone detection refresh)."""
    uri = params.text_document.uri
    source = params.text if params.text else None
    if source is None:
        # Read from disk if text not included
        try:
            filepath = uri
            if filepath.startswith("file:///"):
                filepath = filepath[8:]
            elif filepath.startswith("file://"):
                filepath = filepath[7:]
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception:
            return
    _schedule_analysis(uri, source)


@server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
def on_did_close(params: types.DidCloseTextDocumentParams):
    """Clean up when document is closed."""
    uri = params.text_document.uri
    _workspace_functions.pop(uri, None)
    # Cancel pending analysis
    existing = _debounce_tasks.pop(uri, None)
    if existing and not existing.done():
        existing.cancel()
    # Clear diagnostics
    server.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(uri=uri, diagnostics=[])
    )
    log.info(f"Document closed: {uri}")


# ────────────────────────────────────────────────────────────────
# CodeLens — show clone info above functions
# ────────────────────────────────────────────────────────────────

@server.feature(types.TEXT_DOCUMENT_CODE_LENS)
def on_code_lens(params: types.CodeLensParams) -> List[types.CodeLens]:
    """Provide CodeLens annotations for cloned functions."""
    uri = params.text_document.uri
    lenses: List[types.CodeLens] = []

    # Gather all functions across workspace
    all_functions: List[Dict[str, Any]] = []
    for funcs in _workspace_functions.values():
        all_functions.extend(funcs)

    if len(all_functions) < 2:
        return lenses

    # Find clones for functions in THIS file
    my_functions = _workspace_functions.get(uri, [])
    for func in my_functions:
        code_a = func.get("code", "")
        if not code_a or len(code_a.strip()) < 20:
            continue

        for other in all_functions:
            if other["file"] == uri and other["name"] == func["name"]:
                continue  # skip self
            code_b = other.get("code", "")
            if not code_b or len(code_b.strip()) < 20:
                continue

            score = jaccard_similarity(code_a, code_b)
            if score >= _config["clone_threshold"]:
                # Get a display-friendly filename
                other_file = other["file"]
                if "/" in other_file:
                    other_file = other_file.rsplit("/", 1)[-1]
                elif "\\" in other_file:
                    other_file = other_file.rsplit("\\", 1)[-1]

                line = func.get("start", 0)
                lens = types.CodeLens(
                    range=types.Range(
                        start=types.Position(line=line, character=0),
                        end=types.Position(line=line, character=0),
                    ),
                    command=types.Command(
                        title=f"\U0001f501 Clone of {other_file}:{other['name']} ({int(score * 100)}% similar)",
                        command="",
                    ),
                )
                lenses.append(lens)

    return lenses


# ────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--check" in sys.argv:
        print("IBD LSP Server ready")
        sys.exit(0)

    log.info("Starting IBD LSP Server on stdio...")
    server.start_io()
