# agent_online.py
"""
Optional online AI wrapper. Non-invasive:
- Provides get_online_answer(query) -> str or None
- Chooses provider by env var preference:
    GROQ_API_KEY -> use Groq (template)
    GEMINI_API_KEY -> use Gemini (template)
    OPENAI_API_KEY -> use OpenAI (example)
- If no key or provider call fails -> returns None (so caller can fallback to offline)
"""

import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()            # reads .env into environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_PROJECT = os.environ.get("GEMINI_PROJECT")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# load dotenv if your app uses it
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GROQ_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

TIMEOUT = 15  # seconds

def get_online_answer(query: str) -> Optional[str]:
    """
    Try providers in order; return text answer or None.
    Keep this fast and non-crashing (exceptions -> None).
    """
    if not query:
        return None

    # 1) GROQ (template)
    if GROQ_KEY:
        try:
            return call_groq(query)
        except Exception as e:
            # log to console for debugging; don't raise
            print("GROQ call failed:", e)

    # 2) GEMINI (template)
    if GEMINI_KEY:
        try:
            return _call_gemini(query)
        except Exception as e:
            print("Gemini call failed:", e)

    # 3) OPENAI (example)
    if OPENAI_KEY:
        try:
            return _call_openai(query)
        except Exception as e:
            print("OpenAI call failed:", e)

    return None


# --- Provider implementations (examples / templates) -------------------
def call_groq(query):
    import requests, os

    url = "https://api.groq.com/openai/v1/chat/completions"
    key = os.getenv("GROQ_API_KEY")

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 200
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]



def _call_gemini(query: str) -> str:
    """
    Template for Google Gemini calls. Replace with actual endpoint and auth per Google's docs.
    """
    endpoint = "https://gemini.googleapis.com/v1/models/gemini"  # <-- placeholder
    headers = {
        "Authorization": f"Bearer {GEMINI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": query,
        "maxOutputTokens": 512
    }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    j = resp.json()
    # parse and return a string
    # Update parsing according to Gemini's response shape
    if isinstance(j, dict):
        # examples of fields you might see
        if "candidates" in j and isinstance(j["candidates"], list) and j["candidates"]:
            return j["candidates"][0].get("content", "")
        if "output" in j:
            return str(j["output"])
        return json.dumps(j)
    return str(j)


def _call_openai(query: str) -> str:
    """
    OpenAI example using requests (no dependency on openai package),
    or you can switch to openai.ChatCompletion if you installed openai.
    """
    import os
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_KEY missing")
    # Simple ChatCompletion v1 via requests — adjust if using a different api
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 512,
        "temperature": 0.2,
    }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    j = resp.json()
    # parse ChatCompletion structure
    text = None
    if isinstance(j, dict):
        try:
            text = j["choices"][0]["message"]["content"]
        except Exception:
            # fallback: first choice text
            try:
                text = j["choices"][0].get("text")
            except Exception:
                text = None
    if not text:
        text = json.dumps(j)
    return str(text)


# ----------------- end agent_online.py --------------------------------
