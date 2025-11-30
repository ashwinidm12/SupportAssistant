import importlib, traceback, sys

importlib.invalidate_caches()
try:
    import agent
    print("agent imported successfully.")
    # list the important names (if defined)
    names = [n for n in dir(agent) if n in ("load_faqs","load_dataset_csv","build_suggestions","generate_response","should_escalate","Agent","make_agent","_get_agent")]
    print("Available names:", names)
    if hasattr(agent, "load_faqs"):
        faqs = agent.load_faqs()
        print("load_faqs() returned type:", type(faqs), "len:", len(faqs))
except Exception:
    print("IMPORT TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)
