# app.py (robust / fallback-friendly version)
# CRITICAL: set_page_config MUST be the very first Streamlit command
import streamlit as st
st.set_page_config(page_title="Support Assistant", layout="wide", initial_sidebar_state="expanded")

from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# Compatibility rerun
if hasattr(st, 'rerun'):
    rerun = st.rerun
else:
    rerun = st.experimental_rerun

# UI / voice / agent imports (these are optional and the code will tolerate missing features)
from ui_components import (
    render_css,
    render_header,
    render_sidebar_chat_history,
    render_chat_stream,
    render_faq_suggestions,
    render_quick_help,
)
# voice_mic.render_whatsapp_mic is optional; import safely
try:
    from voice_mic import render_whatsapp_mic
except Exception:
    render_whatsapp_mic = None

# agent import (offline agent)
try:
    from agent import Agent
except Exception as e:
    Agent = None
    print("agent import failed:", e)

# optional online wrapper
try:
    from agent_online import get_online_answer
except Exception:
    get_online_answer = None

# hide default Streamlit chrome
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# apply CSS
render_css()

# start local upload server if available (non-fatal)
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
try:
    import upload_server
    os.makedirs(uploads_dir, exist_ok=True)
    try:
        upload_server.start_upload_server()
    except Exception:
        # ignore if upload server not available or already running
        pass
except Exception:
    # upload_server optional
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

# initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""
if "input_clear_counter" not in st.session_state:
    st.session_state.input_clear_counter = 0
if "agent" not in st.session_state:
    if Agent:
        try:
            st.session_state.agent = Agent()
        except Exception as e:
            # fallback to None and continue (UI will still load)
            st.session_state.agent = None
            st.error(f"Warning: failed to initialize agent: {e}")
    else:
        st.session_state.agent = None

agent = st.session_state.agent

# render header (the actual header/avatar is inside chat stream)
# pass None so ui_components uses its default avatars if agent lacks config
try:
    assistant_avatar = getattr(agent, "config", None) and getattr(agent.config, "ASSISTANT_AVATAR", None)
except Exception:
    assistant_avatar = None

# Header & Sidebar
render_header("Support Assistant", avatar_url=assistant_avatar)
render_sidebar_chat_history(st.session_state.history)

# Main layout: chat + right info
main_col1, main_col2 = st.columns([3, 1])

with main_col1:
    # chat stream - let ui_components choose default avatars if None
    try:
        render_chat_stream(
            st.session_state.history,
            assistant_avatar=assistant_avatar,
            user_avatar=None
        )
    except Exception as e:
        st.error(f"Chat stream error: {e}")

    # 3x3 suggestion chips (render_faq_suggestions handles layout)
    try:
        render_faq_suggestions(agent)
    except Exception:
        # fail silently - suggestions must not break app
        pass

    # Attempt to render mic; but tolerate missing voice_mic implementation
    transcript = None
    if render_whatsapp_mic:
        try:
            # render_whatsapp_mic returns transcript or None
            transcript = render_whatsapp_mic()
        except Exception as e:
            # show a small debug message in the UI (non-fatal)
            st.warning("Microphone unavailable (JS or dependencies).")
            transcript = None

    # WhatsApp-style input block (emoji/plus, text input, mic, send)
    st.markdown("""
    <div class="whatsapp-input-wrapper">
      <div id="whatsapp-input-container">
    """, unsafe_allow_html=True)

    # create columns for input: left (plus), middle (text input), small (mic), right (send)
    col_a, col_b, col_c, col_d = st.columns([0.6, 8, 0.8, 1.0])

    with col_a:
        # plus icon triggers hidden file uploader (if you wired JS), but we keep visual
        st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:100%'><div class='input-plus' title='Attach'>＋</div></div>", unsafe_allow_html=True)

    with col_b:
        # text input; using text_area would allow multi-line, adjust as you like
        if "pending_input" not in st.session_state:
            st.session_state.pending_input = ""
        qkey = f"input_box_{st.session_state.input_clear_counter}"
        q = st.text_input("", value=st.session_state.pending_input, key=qkey, placeholder="Type a message", label_visibility="collapsed")

    with col_c:
        # mic fallback: if render_whatsapp_mic already ran above and returned transcript,
        # show a small badge; otherwise show a compact mic button for user
        try:
            if transcript:
                st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:100%'><div class='mic-compact'>🎤</div></div>", unsafe_allow_html=True)
            else:
                # render a clickable mic control; clicking won't break if recorder missing
                st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:100%'><button class='mic-compact'>🎤</button></div>", unsafe_allow_html=True)
        except Exception:
            pass

    with col_d:
        # Send button
        if st.button("Send", key="send_btn", use_container_width=True):
            if q and q.strip():
                # append user's message and a typing indicator
                st.session_state.history.append(("user", q.strip(), datetime.now()))
                st.session_state.history.append(("assistant", "Assistant is typing...", datetime.now()))
                st.session_state.pending_input = ""
                st.session_state.input_clear_counter += 1
                st.session_state.processing = True
                # trigger rerun so the processing block can run
                rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

with main_col2:
    render_quick_help()

# if microphone produced a transcript, add it to history and trigger processing
if transcript:
    st.session_state.history.append(("user", transcript, datetime.now()))
    st.session_state.history.append(("assistant", "Assistant is typing...", datetime.now()))
    st.session_state.pending_input = ""
    st.session_state.processing = True
    rerun()

# Process typing indicator and generate a response (single-step, tolerant)
def produce_agent_response(user_q: str):
    """
    Try to get an answer from:
      1) online providers via get_online_answer (if present)
      2) agent.handle_query(user_q) if available
      3) agent.generate_response(user_q) or agent.answer(user_q)
      4) fallback reply
    Returns (text, metadata)
    """
    # 1) try online wrapper if available
    if get_online_answer:
        try:
            online = get_online_answer(user_q)
            if online:
                return online, {"source": "online"}
        except Exception:
            pass

    # 2) if agent has handle_query (which may return (text, metadata))
    if agent:
        try:
            if hasattr(agent, "handle_query"):
                out = agent.handle_query(user_q)
                # handle_query may return (text, meta) or just text
                if isinstance(out, tuple) and len(out) >= 1:
                    txt = out[0]
                    meta = out[1] if len(out) > 1 else {}
                    return txt, meta
                else:
                    return str(out), {}
        except Exception:
            # swallow and try other ways
            pass

        # 3) try generate_response / answer
        try:
            if hasattr(agent, "generate_response"):
                txt = agent.generate_response(user_q)
                return txt, {"source": "agent.generate_response"}
            if hasattr(agent, "answer"):
                txt = agent.answer(user_q)
                return txt, {"source": "agent.answer"}
        except Exception:
            pass

    # final fallback
    return "Sorry — I don't have an answer right now. Please contact support.", {"source": "fallback"}

# If last message is the typing indicator, produce a response
if st.session_state.history and st.session_state.history[-1][1] == "Assistant is typing...":
    # ensure there is a user question before the typing indicator
    if len(st.session_state.history) >= 2 and st.session_state.history[-2][0] == "user":
        user_q = st.session_state.history[-2][1]
        try:
            resp_text, metadata = produce_agent_response(user_q)
            # replace typing indicator with actual assistant message
            st.session_state.history[-1] = ("assistant", resp_text, datetime.now())
            st.session_state.processing = False
            # optional: store metadata somewhere if you want
            rerun()
        except Exception as e:
            st.session_state.history[-1] = ("assistant", f"Error generating response: {e}", datetime.now())
            st.session_state.processing = False
            rerun()
