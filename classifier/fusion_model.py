"""
Simple fusion model: computes a combined "suspicion score" using:
- structural similarity (percentage match on basic features)
- semantic similarity (embedding cosine)
- dynamic anomaly flag
No training here; just a weighted scoring mechanism for prototype demonstration.
"""
import math

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
    Weighted sum -> 0..1
    struct_sim, semantic_sim are [0..1], dynamic_anomaly is 0 or 1
    """
    w_s, w_sem, w_d = weights
    score = w_s*struct_sim + w_sem*semantic_sim + w_d*(1.0 if dynamic_anomaly else 0.0)
    # ensure in 0..1
    return max(0.0, min(1.0, score))

def fusion_score_detailed(struct_sim, semantic_sim, dynamic_anomaly, weights=(0.3, 0.5, 0.2)):
    """
    Returns (score, components_dict, explanation_str)
    """
    w_s, w_sem, w_d = weights
    
    comp_struct = w_s * struct_sim
    comp_sem = w_sem * semantic_sim
    comp_dyn = w_d * (1.0 if dynamic_anomaly else 0.0)
    
    score = comp_struct + comp_sem + comp_dyn
    score = max(0.0, min(1.0, score))
    
    components = {
        "structural": struct_sim,
        "semantic": semantic_sim,
        "dynamic": dynamic_anomaly,
        "weighted_structural": comp_struct,
        "weighted_semantic": comp_sem,
        "weighted_dynamic": comp_dyn
    }
    
    # Generate simple explanation
    reasons = []
    if semantic_sim > 0.8:
        reasons.append(f"High semantic similarity ({semantic_sim:.2f})")
    elif semantic_sim > 0.5:
        reasons.append(f"Moderate semantic similarity ({semantic_sim:.2f})")
        
    if struct_sim > 0.8:
        reasons.append(f"High structural match ({struct_sim:.2f})")
        
    if dynamic_anomaly:
        reasons.append("Dynamic execution anomaly detected")
        
    explanation = "Clone detected due to: " + ", ".join(reasons)
    
    return score, components, explanation

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
