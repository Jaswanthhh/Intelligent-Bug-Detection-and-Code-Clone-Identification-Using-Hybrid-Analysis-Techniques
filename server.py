import os
import asyncio
import uuid
import json
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import shutil
import git

# Import the existing pipeline
from main import run_pipeline

app = FastAPI(title="Intelligent Bug Detection API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Intelligent Bug Detection API is running",
        "docs": "/docs",
        "health": "/health"
    }

# In-memory job store
jobs: Dict[str, Dict[str, Any]] = {}
executor = ThreadPoolExecutor(max_workers=2)

class AnalyzeRequest(BaseModel):
    paths: List[str] = [] # Changed to optional default
    github_url: Optional[str] = None # NEW: GitHub URL support
    semantic_threshold: float = 0.1
    dynamic_runs: int = 5
    enable_bci: bool = False

class RepairRequest(BaseModel):
    bug_description: str
    code_snippet: str
    language: str = "python"

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ...

def run_analysis_task(job_id: str, request: AnalyzeRequest):
    temp_dir = None
    try:
        jobs[job_id]["status"] = "running"
        
        target_paths = request.paths
        repo_name = "Local Project"

        # Handle GitHub URL
        if request.github_url:
            print(f"[{job_id}] Cloning GitHub Repo: {request.github_url}")
            repo_name = request.github_url.split("/")[-1].replace(".git", "")
            temp_dir = os.path.join("temp_repos", job_id)
            
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            git.Repo.clone_from(request.github_url, temp_dir)
            target_paths = [temp_dir]
            print(f"[{job_id}] Cloned to {temp_dir}")
        
        print(f"[{job_id}] Starting analysis on {target_paths}")
        
        # Check if paths exist
        for p in target_paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Path not found: {p}")

        raw_results = run_pipeline(
            paths=target_paths,
            semantic_threshold=request.semantic_threshold,
            dynamic_runs=request.dynamic_runs,
            enable_bci=request.enable_bci,
            show_progress=False, # Disable tqdm for API
            verbose=True
        )
        
        # Format results to match CLI JSON output structure
        formatted_results = {
            "metadata": {
                "paths": target_paths,
                "github_url": request.github_url,
                "code_folder": repo_name, # Use repo name for display
                "semantic_threshold": request.semantic_threshold,
                "dynamic_runs": request.dynamic_runs,
                "enable_bci": request.enable_bci,
                "timestamp": str(time.time())
            },
            # ... (Rest of formatting remains same)
            "static_analysis": {
                "total_files": len(raw_results["static"]),
                "files": raw_results["static"]
            },
            "semantic_analysis": {
                "total_pairs": len(raw_results["semantic_pairs"]),
                "pairs": raw_results["semantic_pairs"]
            },
            "dynamic_testing": {
                "total_files_tested": len(raw_results["dynamic"]),
                "results": raw_results["dynamic"]
            },
            "bci_tracing": {
                "total_files_traced": len(raw_results["bci"]),
                "results": raw_results["bci"]
            },
            "fusion_reports": {
                "total_reports": len(raw_results["reports"]),
                "reports": raw_results["reports"]
            },
            "summary_statistics": {
                "total_files": len(raw_results["static"]),
                "total_clone_pairs": len(raw_results["semantic_pairs"]),
                "total_reports": len(raw_results["reports"]),
                "files_with_anomalies": len([r for r in raw_results["dynamic"] if r.get("anomalies")]),
                "total_anomalies": sum(len(r.get("anomalies", [])) for r in raw_results["dynamic"])
            },
            "bug_detection": {
                "total_bugs": len(raw_results.get("bugs", [])),
                "stats": raw_results.get("bug_stats", {}),
                "bugs": raw_results.get("bugs", [])
            }
        }
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = formatted_results
        print(f"[{job_id}] Analysis complete")
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        print(f"[{job_id}] Analysis failed: {e}")
    finally:
        # Auto-cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Grant permission to delete read-only files (common in .git folders)
                def on_rm_error(func, path, exc_info):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    os.unlink(path)
                
                shutil.rmtree(temp_dir, onerror=on_rm_error)
                print(f"[{job_id}] Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_error:
                print(f"[{job_id}] Warning: Cleanup failed: {cleanup_error}")


@app.post("/analyze", response_model=JobStatus)
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "request": request.dict(),
        "created_at": str(asyncio.get_event_loop().time())
    }
    
    # Run in background thread to not block the event loop
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run_analysis_task, job_id, request)
    
    return JobStatus(job_id=job_id, status="pending")

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error")
    )

@app.get("/fs/list")
async def list_filesystem(path: str = "."):
    try:
        # Security: Prevent escaping restricted directories if needed (omitted for prototype)
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="Path not found")
        
        items = []
        # Parent directory
        parent = os.path.dirname(abs_path)
        items.append({"name": "..", "path": parent, "is_dir": True})
        
        with os.scandir(abs_path) as it:
            for entry in it:
                items.append({
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": entry.is_dir()
                })
        
        # Sort: Directories first, then files
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return {"current_path": abs_path, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/read")
async def read_file(path: str):
    try:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Basic security check (optional for prototype)
        # if "prototype" not in abs_path: ...

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        return {"path": abs_path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SettingsRequest(BaseModel):
    api_key: str
    provider: str = "openai" # or "gemini"

import httpx

# ... (existing imports)

# ...

# In-memory settings
# In-memory settings
settings = {
    "api_key": "AIzaSyD3kVJ8jzSaSaS_x3eJQzexzc2g2oXXXXX", 
    "provider": "gemini"
}

@app.post("/settings")
async def update_settings(request: SettingsRequest):
    settings["api_key"] = request.api_key
    settings["provider"] = request.provider
    return {"status": "updated"}
# Response cache for Gemini repairs (avoids duplicate API calls)
import hashlib
repair_cache: Dict[str, str] = {}

@app.post("/repair")
async def suggest_repair(request: RepairRequest):
    """Use Gemini SDK to generate a real fix for the detected bug."""
    try:
        # 1. Read the original source file to give Gemini full context
        source_code = ""
        if hasattr(request, 'code_snippet') and request.code_snippet and request.code_snippet != "Code snippet not available in prototype":
            source_code = request.code_snippet
        else:
            source_code = "(Full source not available — analyzing based on bug description)"

        # 2. Check cache first — same bug + code = same fix
        cache_key = hashlib.md5(f"{request.bug_description}:{source_code[:500]}".encode()).hexdigest()
        if cache_key in repair_cache:
            print(f"[CACHE HIT] Returning cached repair for: {request.bug_description[:50]}")
            return {"suggestion": repair_cache[cache_key]}

        # 3. Call Gemini via official SDK (handles rate limits automatically)
        if settings["api_key"] and settings["provider"] == "gemini":
            import google.generativeai as genai
            
            genai.configure(api_key=settings["api_key"])
            model = genai.GenerativeModel("gemma-3-4b-it")
            
            prompt = f"""You are a senior software engineer. Analyze this bug and provide ONLY the corrected, complete source code.

BUG DESCRIPTION: {request.bug_description}

CODE WITH BUG:
{source_code}

INSTRUCTIONS:
- Return ONLY the fixed code, no explanations before or after
- Fix the specific bug described
- Keep all other code exactly the same
- Add a comment "# FIXED:" next to each line you changed
"""
            # Run in thread pool to avoid blocking the event loop
            import functools
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    model.generate_content,
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=4096
                    )
                )
            )
            
            suggestion = response.text
            # Cache the result
            repair_cache[cache_key] = suggestion
            print(f"[CACHE STORE] Cached repair for: {request.bug_description[:50]}")
            return {"suggestion": suggestion}

        # Fallback mock
        await asyncio.sleep(1)
        suggestion = f"""# Suggested Fix (No API Key configured)
# Bug: {request.bug_description}
# Please configure your Gemini API key via /settings endpoint
"""
        return {"suggestion": suggestion}
        
    except Exception as e:
        print(f"Repair error: {e}")
        return {"suggestion": f"AI Error: {str(e)}"}

class ApplyFixRequest(BaseModel):
    path: str
    content: str

@app.post("/apply_fix")
async def apply_fix(request: ApplyFixRequest):
    """Save the corrected code to corrected_code/ folder. NEVER modify originals."""
    print(f"Saving corrected version for: {request.path}")
    try:
        # 1. Determine the corrected_code folder (at project root level)
        # request.path is something like: C:\...\prototype\samples\sample_buggy.py
        # We want to save to: C:\...\prototype\corrected_code\sample_buggy.py
        
        original_path = request.path
        
        # Find the base project directory (where server.py lives)
        project_root = os.path.dirname(os.path.abspath(__file__))
        corrected_dir = os.path.join(project_root, "corrected_code")
        
        # Create corrected_code/ folder if it doesn't exist
        os.makedirs(corrected_dir, exist_ok=True)
        
        # Get just the filename from the original path
        original_filename = os.path.basename(original_path)
        name, ext = os.path.splitext(original_filename)
        
        # Create the corrected filename with timestamp to avoid overwrites
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        corrected_filename = f"{name}_fixed_{timestamp}{ext}"
        corrected_path = os.path.join(corrected_dir, corrected_filename)
        
        # 2. Extract code from markdown if present (Gemini sometimes wraps in ```)
        content = request.content
        if "```" in content:
            import re
            match = re.search(r"```(?:\w+)?\n(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1)
        
        # 3. Add header comment to the fixed file
        header = f"""# ===================================================
# CORRECTED FILE - Generated by IBD AI (Gemini)
# Original: {original_path}
# Fixed on: {time.strftime("%Y-%m-%d %H:%M:%S")}
# ===================================================

"""
        final_content = header + content.strip() + "\n"
        
        # 4. Write to corrected_code/ folder
        with open(corrected_path, "w", encoding="utf-8") as f:
            f.write(final_content)
            
        print(f"Corrected file saved to: {corrected_path}")
        return {
            "status": "success", 
            "corrected_path": corrected_path,
            "original_path": original_path,
            "message": f"Fixed code saved to corrected_code/{corrected_filename}"
        }
    except Exception as e:
        print(f"Error applying fix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}


class FileRequest(BaseModel):
    path: str
    content: Optional[str] = None

@app.post("/analyze_file")
async def analyze_single_file(request: FileRequest):
    """
    Lightweight analysis for a single file (IDE mode).
    """
    try:
        # Save content temporarily if provided (simulating unsaved buffer)
        target_path = request.path
        if request.content:
            # We analyze the content, but for simplicity in prototype, 
            # we might just analyze the file on disk if it matches.
            # Ideally, we'd pass content string to parsers directly.
            pass

        if not os.path.exists(target_path):
             return {"issues": []}

        issues = []
        
        # Read the file from disk
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Lightweight static pattern detection (fast for IDE use)
        lines = code.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Security checks
            if "eval(" in line:
                issues.append({"line": i+1, "message": "Avoid using eval() - Security Risk (use ast.literal_eval instead)", "severity": "critical", "type": "Security"})
            if "exec(" in line:
                issues.append({"line": i+1, "message": "Avoid using exec() - Code Injection Risk", "severity": "critical", "type": "Security"})
            if "os.system(" in line:
                issues.append({"line": i+1, "message": "Avoid os.system() - Use subprocess instead", "severity": "high", "type": "Security"})
            if "pickle.loads(" in line or "pickle.load(" in line:
                issues.append({"line": i+1, "message": "Deserializing untrusted data with pickle is dangerous", "severity": "critical", "type": "Security"})
            # Best practice checks
            if stripped == "except:":
                issues.append({"line": i+1, "message": "Avoid bare 'except:' clause - catch specific exceptions", "severity": "medium", "type": "Best Practice"})
            if "import *" in line:
                issues.append({"line": i+1, "message": "Avoid wildcard imports (import *)", "severity": "low", "type": "Best Practice"})
            # Common bug patterns
            if "== None" in line or "!= None" in line:
                issues.append({"line": i+1, "message": "Use 'is None' / 'is not None' instead of == / !=", "severity": "low", "type": "Style"})
            if "while True:" in stripped and "break" not in code:
                issues.append({"line": i+1, "message": "Potential infinite loop (no break found)", "severity": "high", "type": "Logic"})
            
        return {"issues": issues}
        
    except Exception as e:
        print(f"Analyze File Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repair_file_safe")
async def repair_file_safe(request: FileRequest):
    """
    Generates a fixed copy of the file (APR Safe Mode).
    """
    try:
        original_path = request.path
        if not os.path.exists(original_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        dir_name = os.path.dirname(original_path)
        base_name = os.path.basename(original_path)
        name, ext = os.path.splitext(base_name)
        
        fixed_filename = f"{name}_fixed{ext}"
        fixed_path = os.path.join(dir_name, fixed_filename)
        
        # 1. Get Code
        code = request.content if request.content else ""
        if not code:
            with open(original_path, 'r', encoding='utf-8') as f:
                code = f.read()

        # 2. Simulate AI Repair (Mock or Real)
        # In real system, we'd call Mistral/GPT here
        fixed_code = code + "\n\n# Fixed by IBD AI\n# (No critical bugs found, this is a verify copy)"
        
        # Simple specific fix for demo
        if "eval(" in fixed_code:
            fixed_code = fixed_code.replace("eval(", "ast.literal_eval(")
            fixed_code = "import ast\n" + fixed_code
            
        # 3. Write to Copy
        with open(fixed_path, "w", encoding='utf-8') as f:
            f.write(fixed_code)
            
        return {"fixed_path": fixed_path, "status": "created"}

    except Exception as e:
        print(f"Repair Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

