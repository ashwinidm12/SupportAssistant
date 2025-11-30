# generate_faqs_offline_full.py
"""
Offline FAQ generator - creates a large FAQ file (data/faqs_large.json) from a small seed.
This is deterministic-ish and safe for demos (no API calls).
"""
import os, json, random, itertools
random.seed(42)

DATA_DIR = "data"
OUT_PATH = os.path.join(DATA_DIR, "faqs_large.json")
SEED_PATH = os.path.join(DATA_DIR, "faqs_large.json") if os.path.exists(os.path.join(DATA_DIR, "faqs_large.json")) else os.path.join(DATA_DIR, "faqs.json")

os.makedirs(DATA_DIR, exist_ok=True)

# default seed if none exists
default_seed = [
  {"question":"How do I reset my password?", "answer":"Go to Settings → Account → Reset Password. You will receive a reset link on your registered email."},
  {"question":"What are the working hours?", "answer":"Our standard working hours are Monday to Friday, 9:30 AM to 6:30 PM."},
  {"question":"How do I request leave?", "answer":"Open the HR portal, select Leave Request, choose dates and reason, then submit. Your manager will be notified."},
  {"question":"Who do I contact for payroll issues?", "answer":"Please email payroll@company.com with your employee ID and the payroll month in the subject line."}
]

# load seed
if os.path.exists(SEED_PATH):
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            seed = json.load(f)
            if not isinstance(seed, list) or len(seed) == 0:
                seed = default_seed
    except Exception:
        seed = default_seed
else:
    seed = default_seed

# helper functions to create variations
prefixes = ["How do I", "How can I", "Where can I", "What is the process to", "Can I", "Is it possible to", "How to"]
suffixes = ["?", " please?", " ASAP?", " — urgent?"]
templates = [
    ("How do I {action} my {object}?", "To {action} your {object}, go to the dashboard and follow the steps."),
    ("Can I {action} my {object} now?", "If you need to {action} your {object} immediately, contact support and we will assist."),
    ("What is the policy for {topic}?", "The policy for {topic} is available on the company intranet under Policies."),
    ("Who can help with {topic}?", "Contact the {topic} team via support@example.com for help."),
    ("How long does {process} take?", "Typically {process} takes 1-3 business days, depending on approvals."),
]

actions = ["reset", "change", "update", "view", "cancel", "track"]
objects = ["password", "email", "profile", "bank details", "leave request", "order"]
topics = ["leave", "salary", "work from home", "reimbursement", "refund", "returns"]
processes = ["refund processing", "order delivery", "account verification"]

out = []
# include seed
for f in seed:
    q = f.get("question","").strip()
    a = f.get("answer","").strip()
    if q and a:
        out.append({"question": q, "answer": a})

# create paraphrases & template-based items
def make_paraphrases(q, a):
    qs = set()
    qbase = q.rstrip("?")
    qs.add(qbase + "?")
    qs.add("How to " + qbase + "?")
    words = qbase.split()
    if len(words) > 2:
        tail = " ".join(words[1:])
        qs.add("How do I " + tail + "?")
    if "password" in qbase.lower():
        qs.add("I forgot my password — what to do?")
        qs.add("Reset my account password, please.")
    if "order" in qbase.lower():
        qs.add("Where is my order?")
        qs.add("Track my order status.")
    return [{"question":qq, "answer":a} for qq in qs]

# expand using seed paraphrases
for f in seed:
    out.extend(make_paraphrases(f["question"], f["answer"]))

# generate synthetic ones until we reach ~1000 unique questions
attempts = 0
while len(out) < 1000 and attempts < 5000:
    attempts += 1
    t = random.choice(templates)
    if "{object}" in t[0]:
        action = random.choice(actions)
        obj = random.choice(objects)
        q = t[0].format(action=action, object=obj)
        a = t[1].format(action=action, object=obj)
    elif "{topic}" in t[0]:
        top = random.choice(topics)
        q = t[0].format(topic=top)
        a = t[1].format(topic=top)
    else:
        proc = random.choice(processes)
        q = t[0].format(process=proc)
        a = t[1].format(process=proc)
    out.append({"question": q, "answer": a})

# add some shorter commons
shorts = [
    ("What is my leave balance?", "Login to HR portal → Leave Balance to view remaining days."),
    ("How to change bank details?", "Go to Profile → Bank Details → Edit and submit supporting documents."),
    ("How do I get reimbursement?", "Upload bills in the Reimbursements section and submit for manager approval."),
]
for q,a in shorts:
    out.append({"question":q, "answer":a})

# dedupe preserving first occurrence
unique = {}
for item in out:
    key = item["question"].strip()
    if key not in unique:
        unique[key] = item

result = list(unique.values())[:1000]

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT_PATH} ({len(result)} FAQs).")
