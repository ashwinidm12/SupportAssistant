# genai_test.py
import os
from dotenv import load_dotenv
load_dotenv()
try:
    import google.generativeai as genai
    print("Imported google.generativeai, attributes:", [a for a in dir(genai) if a.startswith("generate") or a.startswith("text") or a.startswith("chat")][:20])
    print("genai has generate_text:", hasattr(genai, "generate_text"))
    print("genai has text.generate:", hasattr(getattr(genai, "text", None), "generate") if hasattr(genai, "text") else False)
    print("genai has chat.completions.create:", hasattr(getattr(genai, "chat", None), "completions") if hasattr(genai, "chat") else False)
except Exception as e:
    print("Import or introspection failed:", e)
