"""
Uses sentence-transformers to compute embeddings for code snippets (functions).
Computes pairwise cosine similarities to find candidate clones.
"""
import os
import numpy as np
import difflib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: sentence-transformers not available ({e})")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Force Jaccard fallback for robustness in this prototype environment
SKLEARN_AVAILABLE = False
# try:
#     from sklearn.metrics.pairwise import cosine_similarity
#     from sklearn.feature_extraction.text import TfidfVectorizer
#     SKLEARN_AVAILABLE = True
# except ImportError:
#     print("Warning: sklearn not available")
#     SKLEARN_AVAILABLE = False

# choose a small model for speed
_MODEL_NAME = "all-MiniLM-L6-v2"

# lazy-loaded model
_model = None

def _get_model():
    global _model
    if _model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model

def embed_snippets(snippets, show_progress=False):
    """
    snippets: list of strings (code text)
    returns np.array embeddings (n x d) or None if no embedding method available
    """
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        model = _get_model()
        emb = model.encode(snippets, show_progress_bar=show_progress)
        return np.array(emb)
    elif SKLEARN_AVAILABLE:
        # Fallback: simple character-level embeddings
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 3))
        emb = vectorizer.fit_transform(snippets).toarray()
        return emb
    else:
        return None

def find_similar_pairs(snippet_records, top_k=5, threshold=0.75, show_progress=False):
    """
    snippet_records: list of dicts {"file":..., "func_name":..., "code":...}
    returns list of pairs (i, j, score) where score >= threshold
    """
    if len(snippet_records) < 2:
        return []
    
    texts = [r["code"] if r.get("code") else f"{r.get('file')}::{r.get('func_name')}" for r in snippet_records]
    pairs = []
    n = len(texts)
    
    embs = embed_snippets(texts, show_progress=show_progress)
    
    if embs is not None and SKLEARN_AVAILABLE:
        # Use cosine similarity with embeddings
        sims = cosine_similarity(embs)
        
        # Calculate total pairs for progress bar
        total_pairs = n * (n - 1) // 2
        
        if show_progress:
            try:
                from tqdm import tqdm
                pair_iter = tqdm(range(n), desc="Finding similar pairs", unit="snippet")
            except ImportError:
                pair_iter = range(n)
        else:
            pair_iter = range(n)
        
        for i in pair_iter:
            for j in range(i+1, n):
                score = float(sims[i,j])
                if score >= threshold:
                    pairs.append({"i": i, "j": j, "score": score,"a": snippet_records[i], "b": snippet_records[j]})
    else:
        # Fallback: Jaccard Similarity (Token-based)
        # Robust against reordering and minor edits, and works without heavy ML libs.
        import re
        print("Using Jaccard Similarity fallback for clone detection...")
        
        # Pre-tokenize all texts
        token_sets = []
        for text in texts:
            # Split by non-word chars and filter empty
            tokens = set(re.split(r'\W+', text.lower()))
            tokens.discard('')
            token_sets.append(tokens)
            
        for i in range(n):
            for j in range(i+1, n):
                set_a = token_sets[i]
                set_b = token_sets[j]
                
                if not set_a or not set_b:
                    continue
                    
                intersection = len(set_a.intersection(set_b))
                union = len(set_a.union(set_b))
                
                score = intersection / union if union > 0 else 0.0
                
                # Debug print
                if score > 0.1:
                    print(f"DEBUG: Pair {i}-{j} score: {score:.4f} ({texts[i][:20]}... vs {texts[j][:20]}...)")

                if score >= threshold:
                    pairs.append({"i": i, "j": j, "score": score,"a": snippet_records[i], "b": snippet_records[j]})

    # sort by descending score
    pairs.sort(key=lambda x: -x["score"])
    return pairs

if __name__ == "__main__":
    # small self-test with actual extracted code
    demo = [
        {"file": "samples/sample_safe_1.py", "func_name": "add", "code": "def add(a, b):\n    \"\"\"Simple add\"\"\"\n    return a + b"},
        {"file": "samples/sample_safe_2.py", "func_name": "sum_two", "code": "def sum_two(x, y):\n    return x + y"}
    ]
    print("Testing with demo data:")
    print("Demo snippets:", [d["code"] for d in demo])
    
    # Test with different thresholds
    for threshold in [0.9, 0.7, 0.5, 0.3, 0.1, 0.01]:
        pairs = find_similar_pairs(demo, threshold=threshold)
        print(f"Threshold {threshold}: {len(pairs)} pairs found")
        if pairs:
            print(f"  Pairs: {pairs}")
    
    # Test embedding generation
    texts = [d["code"] for d in demo]
    print(f"\nTexts to embed: {texts}")
    embs = embed_snippets(texts)
    print(f"Embeddings shape: {embs.shape}")
    print(f"Embeddings:\n{embs}")
    
    # Test cosine similarity
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity(embs)
    print(f"Similarity matrix:\n{sims}")
