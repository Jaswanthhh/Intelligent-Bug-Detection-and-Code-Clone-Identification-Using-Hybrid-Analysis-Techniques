"""
Simple fusion model: computes a combined "suspicion score" using:
- structural similarity (percentage match on basic features)
- semantic similarity (embedding cosine)
- dynamic anomaly flag
- BCE-style line and token similarity metrics

No training here; just a weighted scoring mechanism for prototype demonstration.
"""
import math
import re

def tokenize(code):
    """
    Simple tokenizer that splits by whitespace but keeps operators.
    Returns a set of unique tokens for set-based similarity.
    """
    if not code:
        return set()
    # Pattern to match words or non-whitespace symbols
    # \w+ matches words, [^\w\s]+ matches sequences of symbols (like ++, ==, >=)
    tokens = re.findall(r'\w+|[^\w\s]+', code)
    return set(tokens)

def compute_similarity_metrics(code_a, code_b):
    """
    Computes BCE-style similarity metrics.
    Returns: (line_similarity, token_similarity)
    Using Overlap Coefficient: |Intersection| / min(|A|, |B|)
    """
    # Line Similarity
    lines_a = set([l.strip() for l in code_a.splitlines() if l.strip()])
    lines_b = set([l.strip() for l in code_b.splitlines() if l.strip()])
    
    if not lines_a or not lines_b:
        line_sim = 0.0
    else:
        intersection = len(lines_a & lines_b)
        min_len = min(len(lines_a), len(lines_b))
        line_sim = intersection / min_len if min_len > 0 else 0.0

    # Token Similarity
    tokens_a = tokenize(code_a)
    tokens_b = tokenize(code_b)
    
    if not tokens_a or not tokens_b:
        token_sim = 0.0
    else:
        intersection = len(tokens_a & tokens_b)
        min_len = min(len(tokens_a), len(tokens_b))
        token_sim = intersection / min_len if min_len > 0 else 0.0
        
    return line_sim, token_sim

def classify_clone_type(line_sim, token_sim, semantic_sim):
    """
    Classifies clone based on BCE thresholds.
    Returns: (clone_type_str, confidence)
    """
    # Use the max of line/token sim as the syntactic similarity measure
    syntactic_sim = max(line_sim, token_sim)
    
    if syntactic_sim >= 0.95:
        # Identical or near-identical logic
        return "Type 1 (Exact)", 1.0
    elif syntactic_sim >= 0.85:
        # Same structure, renamed variables/identifiers
        return "Type 2 (Renamed)", 0.95
    elif syntactic_sim >= 0.60:
        # Some added/removed statements but generally similar structure
        return "Type 3 (Modified)", 0.85
    elif semantic_sim >= 0.75:
        # Low structural match, but High semantic match
        return "Type 4 (Semantic)", semantic_sim
    else:
        return "Non-Clone", 0.0

def structural_similarity(f_a, f_b):
    # f_a and f_b are feature dicts e.g. {"num_statements":..., "num_branches":...}
    keys = set(f_a.keys()) & set(f_b.keys())
    if not keys:
        return 0.0
    diffs = []
    for k in keys:
        a = float(f_a.get(k, 0))
        b = float(f_b.get(k, 0))
        if a + b == 0:
            diffs.append(0.0)
        else:
            diffs.append(1.0 - abs(a - b) / (max(a, b) + 1e-6))
    return sum(diffs) / len(diffs)

def fusion_score(struct_sim, semantic_sim, dynamic_anomaly, weights=(0.3, 0.5, 0.2)):
    """
    Legacy wrapper for backward compatibility.
    """
    return fusion_score_detailed(struct_sim, semantic_sim, dynamic_anomaly, code_a="", code_b="", weights=weights)[0]

def fusion_score_detailed(struct_sim, semantic_sim, dynamic_anomaly, code_a="", code_b="", weights=(0.3, 0.5, 0.2)):
    """
    Returns (score, components_dict, explanation_str)
    Now uses code content to calculate BCE metrics.
    """
    w_s, w_sem, w_d = weights
    
    # 1. Compute BCE metrics
    if code_a and code_b:
        line_sim, token_sim = compute_similarity_metrics(code_a, code_b)
        clone_type, type_conf = classify_clone_type(line_sim, token_sim, semantic_sim)
    else:
        # Fallback if code not provided (legacy behavior)
        line_sim, token_sim = 0.0, 0.0
        clone_type, type_conf = "Unknown (No Code)", 0.0

    # 2. Adjust Score logic
    # If it's a strong syntactic match (Type-1/2/3-Strong), boost the score towards 1.0
    syntactic_sim = max(line_sim, token_sim)
    
    # Base score from features
    base_score = w_s * struct_sim + w_sem * semantic_sim + w_d * (1.0 if dynamic_anomaly else 0.0)
    
    # Boost based on precise syntax
    if syntactic_sim > 0.7:
        # Strong syntax overrides everything
        final_score = max(base_score, syntactic_sim)
    elif semantic_sim > 0.8:
        # Strong semantic overrides weak syntax (Type-4)
        final_score = max(base_score, semantic_sim)
    else:
        final_score = base_score

    final_score = max(0.0, min(1.0, final_score))
    
    components = {
        "structural": struct_sim,
        "semantic": semantic_sim,
        "dynamic": dynamic_anomaly,
        "line_similarity": line_sim,
        "token_similarity": token_sim,
        "clone_type": clone_type,
        "weighted_structural": w_s * struct_sim,
        "weighted_semantic": w_sem * semantic_sim,
        "weighted_dynamic": w_d * (1.0 if dynamic_anomaly else 0.0)
    }
    
    # Generate enhanced explanation
    reasons = []
    reasons.append(f"Classified as {clone_type}")
    
    if syntactic_sim > 0.8:
        reasons.append(f"High syntactic match ({syntactic_sim:.2f})")
    elif semantic_sim > 0.8:
        reasons.append(f"High semantic match ({semantic_sim:.2f})")
        
    if dynamic_anomaly:
        reasons.append("Dynamic execution anomaly detected")
        
    explanation = "Clone detected: " + ", ".join(reasons)
    
    return final_score, components, explanation

# utilities to build snippet records from AST results
def build_snippet_records(static_results):
    """
    static_results: output of scan_code_folder
    returns list of {"file":..., "func_name":..., "code":..., "features": ...}
    """
    recs = []
    for f in static_results:
        path = f.get("path")
        if path.endswith(".py"):
            for fn in f.get("functions", []):
                recs.append({
                    "file": path,
                    "func_name": fn.get("name"),
                    "code": fn.get("code") or "",
                    "features": fn.get("features") or {}
                })
        elif path.endswith(".java"):
            for m in f.get("methods", []):
                recs.append({
                    "file": path,
                    "func_name": m.get("name"),
                    "code": m.get("code") or "",
                    "features": m.get("features") or {}
                })
    return recs

