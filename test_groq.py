# test_groq.py
import os, requests, json
key = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/chat/completions"
hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {
  "model":"llama3-70b-8192",
  "messages":[{"role":"user","content":"Where is my order?"}],
  "max_tokens":50
}
r = requests.post(url, json=payload, headers=hdr, timeout=30)
print(r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
