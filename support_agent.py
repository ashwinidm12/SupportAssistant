# support_agent.py
import os
import json
import time
import traceback
from typing import List, Dict, Tuple

# load .env
from dotenv import load_dotenv
load_dotenv()

# config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-mini")
FAST_MODE = os.environ.get("FAST_MODE", "false").lower() in ("1", "true", "yes")

# attempt to initialize Gemini client (google-generativeai)
genai = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print("Warning: google-generativeai init failed:", e)
        genai = None

# Try to import FAISS + sentence-transformers; if not available use TF-IDF fallback
USE_FAISS = False
_embed_model = None
_faiss_index = None
_faq_texts = []
_faqs = []

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    import numpy as np
    USE_FAISS = True
    print("FAISS available — will use FAISS vector search.")
except Exception as e:
    print("FAISS not available or failed to import (falling back to TF-IDF).", e)
    USE_FAISS = False

# TF-IDF fallback
_tfidf_vectorizer = None
_tfidf_matrix = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_faqs(path_primary="data/faqs_large.json", path_fallback="data/faqs.json") -> List[Dict]:
    path = path_primary if os.path.exists(path_primary) else path_fallback
    if not os.path.exists(path):
        print(f"No FAQ file found at {path_primary} or {path_fallback}. Returning empty list.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        faqs = json.load(f)
    return faqs

def _prepare_faiss(faqs: List[Dict]):
    global _embed_model, _faiss_index, _faq_texts
    if not USE_FAISS:
        return
    try:
        # load embedder
        if _embed_model is None:
            _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        _faq_texts = [f.get("question","") + " " + f.get("answer","") for f in faqs]
        embs = _embed_model.encode(_faq_texts, convert_to_numpy=True, show_progress_bar=True)
        d = embs.shape[1]
        # create FAISS index (IndexFlatIP on normalized vectors or IndexFlatL2)
        # we'll normalize vectors and use inner product for cosine-sim
        # normalize
        import numpy as np
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms[norms==0] = 1.0
        embs_norm = embs / norms
        _faiss_index = faiss.IndexFlatIP(d)
        _faiss_index.add(embs_norm)
        print("FAISS index built with", _faiss_index.ntotal, "vectors.")
    except Exception as e:
        print("Error preparing FAISS index:", e)
        traceback.print_exc()

def _prepare_tfidf(faqs: List[Dict]):
    global _tfidf_vectorizer, _tfidf_matrix
    texts = [f.get("question","") + " " + f.get("answer","") for f in faqs]
    _tfidf_vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words="english", max_features=50000)
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(texts)
    print("TF-IDF prepared with shape:", _tfidf_matrix.shape)

def build_index(faqs: List[Dict]):
    global _faq_texts, _faiss_index, _tfidf_matrix
    if not faqs:
        return
    if USE_FAISS:
        try:
            _prepare_faiss(faqs)
            return
        except Exception as e:
            print("FAISS build error; falling back to TF-IDF:", e)
    # TF-IDF fallback
    _prepare_tfidf(faqs)

def find_similar_faqs(query: str, faqs: List[Dict], top_k: int = 5) -> List[Tuple[float, Dict]]:
    """
    Returns list of (score, faq) sorted by score desc.
    If FAISS available, uses embeddings; else uses TF-IDF cosine.
    """
    if not faqs or not query:
        return []
    # FAISS path
    if USE_FAISS and _faiss_index is not None:
        try:
            q_emb = _embed_model.encode([query], convert_to_numpy=True)
            import numpy as np
            q_norm = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-9)
            D, I = _faiss_index.search(q_norm, top_k)
            results = []
            for score, idx in zip(D[0], I[0]):
                if idx < 0 or idx >= len(faqs):
                    continue
                results.append((float(score), faqs[idx]))
            return results
        except Exception as e:
            print("Error searching FAISS:", e)
    # TF-IDF fallback
    if _tfidf_vectorizer is None or _tfidf_matrix is None:
        _prepare_tfidf(faqs)
    q_vec = _tfidf_vectorizer.transform([query])
    cos_sim = linear_kernel(q_vec, _tfidf_matrix).flatten()
    top_idx = cos_sim.argsort()[::-1][:top_k]
    results = []
    for idx in top_idx:
        score = float(cos_sim[idx])
        if score > 0:
            results.append((score, faqs[idx]))
    return results

def should_escalate(user_query: str) -> bool:
    sensitive = [
        "salary", "pay", "payroll", "termination", "fired", "dismiss",
        "legal", "lawsuit", "notice period", "resign", "disciplinary", "bonus", "ctc", "increment"
    ]
    u = (user_query or "").lower()
    return any(k in u for k in sensitive)

def _call_gemini_system(prompt: str, max_output_tokens: int = 256) -> str:
    """
    Calls Gemini via google-generativeai; returns text or empty string on failure.
    """
    if genai is None:
        return ""
    try:
        # Modern Gemini API (google-generativeai >= 0.3.0)
        model = genai.GenerativeModel(GEMINI_MODEL)
        # If FAST_MODE is enabled, reduce max tokens for quicker responses
        effective_max = max_output_tokens if not FAST_MODE else min(max_output_tokens, 150)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": effective_max,
            }
        )
        # Extract text from response
        txt = ""
        if hasattr(response, 'text'):
            txt = response.text
        elif isinstance(response, str):
            txt = response
        else:
            txt = str(response)
        return txt.strip()
    except Exception as e:
        print("Gemini API error:", e)
        traceback.print_exc()
        return ""

def generate_response(user_query: str, faqs: List[Dict], rows: List[Dict]) -> str:
    """
    Main high-level response function:
    - uses vector search to find matching FAQ(s)
    - if good match found, returns FAQ answer (optionally rewrites via Gemini)
    - else asks Gemini to answer using dataset context (if available) or returns fallback text
    """
    user_q = (user_query or "").strip()
    if not user_q:
        return "Please ask a question."

    # 1) find similar FAQs
    sim = find_similar_faqs(user_q, faqs, top_k=3)
    if sim:
        top_score, top_faq = sim[0]
        # If score is high enough, return FAQ answer directly (prefer speed)
        if USE_FAISS:
            # lower threshold when FAST_MODE to prefer quick FAQ answers
            threshold = 0.4 if not FAST_MODE else 0.35
            if top_score >= threshold:
                return top_faq.get("answer", "")
        else:
            # TF-IDF score: threshold relative
            tf_threshold = 0.05 if not FAST_MODE else 0.03
            if top_score >= tf_threshold:
                return top_faq.get("answer", "")

    # 2) If no strong FAQ match -> check dataset rows for helpful context
    ds_matches = []
    if rows:
        try:
            # simple text overlap search
            uq = set(user_q.lower().split())
            scored = []
            for r in rows:
                text = " ".join([str(v) for v in r.values() if v is not None]).lower()
                score = len(uq & set(text.split()))
                if score > 0:
                    scored.append((score, r))
            scored.sort(reverse=True, key=lambda x: x[0])
            ds_matches = scored[:3]
        except Exception as e:
            print("Dataset search error:", e)

    # 3) If Gemini available, ask it to answer using dataset context and/or FAQ context
    if genai:
        context = ""
        if sim:
            context += "Top matching FAQ:\n"
            for s,f in sim[:2]:
                context += f"Q: {f.get('question')}\nA: {f.get('answer')}\n\n"
        if ds_matches:
            context += "Relevant records:\n"
            for score, row in ds_matches:
                context += json.dumps(row, ensure_ascii=False) + "\n"
        prompt = f"You are a helpful concise employee support assistant. Answer the user question using only the provided context where possible. If no exact info exists, give clear next steps.\n\nContext:\n{context}\nUser question: {user_q}\nAnswer:"
        gen_out = _call_gemini_system(prompt, max_output_tokens=250)
        if gen_out:
            return gen_out

    # 4) fallback: if we had dataset matches return them formatted, else final fallback message
    if ds_matches:
        out_lines = ["I found these relevant records:"]
        for score,row in ds_matches:
            # show a small snippet
            snippet = ", ".join([f"{k}:{v}" for k,v in list(row.items())[:3]])
            out_lines.append(f"- {snippet}")
        return "\n".join(out_lines)

    return "Sorry — I don't have an answer right now. Please contact HR at payroll@company.com."
