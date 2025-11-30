# ui_components.py
import streamlit as st
import html
from datetime import datetime
from typing import List, Optional

# ---- AVATARS ---------------------------------------------------------
# Change these URLs to swap avatars
ASSISTANT_AVATAR = "https://img.icons8.com/fluency/48/chatbot.png"
USER_AVATAR = "https://img.icons8.com/fluency/48/user-male-circle.png"


# ---- GLOBAL CSS (WhatsApp-like layout) ------------------------------
def render_css():
    """Global CSS: WhatsApp-like chat card + bubbles + chips."""
    st.markdown(
        """
        <style>
        :root {
          --primary: #0b73ff;
          --primary-dark: #0056d6;
          --bg-page: #e5ddd5;
          --bg-chat: #efeae2;
          --bubble-user: #0b73ff;
          --bubble-bot: #ffffff;
        }

        /* remove default Streamlit chrome */
        .stApp > header { visibility: hidden; height: 0; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* page background */
        .stApp {
          background: var(--bg-page);
        }

        .main .block-container {
          padding-top: 0.5rem;
          padding-bottom: 110px !important; /* room for bottom input */
        }

        /* chat shell: centred card like WhatsApp Web */
        .chat-shell {
          max-width: 960px;
          margin: 12px auto 0 auto;
          border-radius: 16px;
          background: linear-gradient(180deg, #0c1317 0, #202c33 40px, var(--bg-chat) 40px);
          box-shadow: 0 8px 24px rgba(15,23,42,0.35);
          overflow: hidden;
          border: 1px solid #111827;
        }

        /* header bar inside chat card */
        .chat-top {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 16px;
          background: #202c33;
          color: #e5e7eb;
        }
        .chat-top-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #111827;
          display:flex;
          align-items:center;
          justify-content:center;
          overflow:hidden;
        }
        .chat-top-avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .chat-top-title {
          font-size: 16px;
          font-weight: 600;
        }
        .chat-top-sub {
          font-size: 12px;
          color: #9ca3af;
        }

        /* chat scroll area */
        #chat-container {
          max-height: 60vh;
          min-height: 320px;
          overflow-y: auto;
          padding: 16px 20px 10px 20px;
          background: radial-gradient(circle at top left,#d1f4cc 0,#d1f4cc 200px,var(--bg-chat) 200px);
        }

        /* messages */
        .message {
          display: flex;
          margin-bottom: 10px;
          align-items: flex-end;
          gap: 8px;
        }
        .message.user {
          justify-content: flex-end;
        }
        .message.assistant {
          justify-content: flex-start;
        }

        .message-bubble {
          max-width: 70%;
          padding: 8px 12px;
          border-radius: 12px;
          font-size: 14px;
          line-height: 1.35;
          box-shadow: 0 1px 1px rgba(15,23,42,0.12);
          word-wrap: break-word;
        }

        .message.user .message-bubble {
          background: var(--bubble-user);
          color: #ffffff;
          border-bottom-right-radius: 2px;
        }

        .message.assistant .message-bubble {
          background: var(--bubble-bot);
          color: #111827;
          border-bottom-left-radius: 2px;
        }

        .avatar {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          flex-shrink: 0;
          overflow:hidden;
        }
        .avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .timestamp {
          font-size: 11px;
          color: #9ca3af;
          margin-top: 2px;
          margin-bottom: 6px;
        }
        .message.user + .timestamp {
          text-align: right;
        }

        /* welcome message */
        .welcome {
          text-align: center;
          color: #6b7280;
          padding: 24px 8px 8px 8px;
          font-size: 15px;
        }

        /* suggestion chips row (inside chat shell, under history) */
        .faq-suggestions-wrap {
          padding: 6px 16px 14px 16px;
          /* remove the white horizontal divider that previously showed up */
          border-top: none;
          background: transparent;
        }
        .faq-suggestions {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          align-items: start;
        }
        .faq-chip-btn button {
          background: rgba(255,255,255,0.95) !important;
          border-radius: 999px !important;
          border: 1px solid rgba(148,163,184,0.5) !important;
          font-size: 13px !important;
          padding: 8px 12px !important;
          color: #111827 !important;
          text-align: left !important;
          white-space: normal !important;
        }
        .faq-chip-btn button:hover {
          border-color: var(--primary) !important;
          color: var(--primary) !important;
          box-shadow: 0 4px 12px rgba(37,99,235,0.18) !important;
        }

        /* keep right column simple */
        .stSidebar .sidebar-content { background:white; }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---- HEADER ----------------------------------------------------------
def render_header(title: str = "Support Assistant", avatar_url: Optional[str] = None):
    """
    Minimal compatibility header (top-of-page); the visible chat header is
    rendered inside render_chat_stream.
    """
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)


# ---- SIDEBAR: CHAT HISTORY -------------------------------------------
def render_sidebar_chat_history(history: List[tuple]):
    """Left sidebar with unique recent user questions."""
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        if not history:
            st.info("No conversation history yet.")
            return

        seen = set()
        questions = []
        for role, text, ts in reversed(history):
            if role != "user":
                continue
            if not text or not text.strip():
                continue
            key = text.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            questions.append(text.strip())
            if len(questions) >= 20:
                break

        if not questions:
            st.info("No conversation history yet.")
            return

        for i, q in enumerate(questions):
            label = f"📌 {q[:60]}{'...' if len(q) > 60 else ''}"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state.pending_input = q
                if hasattr(st, "rerun"):
                    st.rerun()
                else:
                    st.experimental_rerun()


# ---- SUGGESTIONS HELPERS --------------------------------------------
def _safe_build_suggestions(agent, limit=9):
    """
    Safely call agent.build_suggestions in multiple possible signatures,
    return up to `limit` unique, non-empty suggestion strings.
    """
    fallback = [
        "How do I place an order?",
        "Refund status",
        "Reset my account password",
        "Payment failed / charged twice",
        "Offers and discounts",
        "How do I request leave?",
        "Who to contact for payroll issues?",
        "What are the working hours?",
        "How can I change my shipping address?"
    ]

    if agent is None:
        return fallback[:limit]

    suggestions = []
    try:
        func = getattr(agent, "build_suggestions", None)
        if callable(func):
            # try multiple call styles
            try:
                suggestions = list(func(limit))
            except TypeError:
                try:
                    suggestions = list(func(top_n=limit))
                except TypeError:
                    try:
                        suggestions = list(func())
                    except Exception:
                        suggestions = []
    except Exception:
        suggestions = []

    # Normalize, dedupe
    clean = []
    seen = set()
    for s in suggestions:
        if not s:
            continue
        t = str(s).strip()
        if not t:
            continue
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        clean.append(t)
        if len(clean) >= limit:
            break

    # Fill from fallback if not enough
    if len(clean) < limit:
        for f in fallback:
            if f.lower() not in seen:
                clean.append(f)
                seen.add(f.lower())
            if len(clean) >= limit:
                break

    return clean[:limit]


def render_faq_suggestions(agent, max_suggestions: int = 9):
    """
    Render suggestion chips in a strict 3-column layout, up to 9 items.
    Clicking a chip puts the text into st.session_state.pending_input and reruns.
    """
    try:
        suggestions = _safe_build_suggestions(agent, limit=max_suggestions)
        if not suggestions:
            return

        # wrapper (no top white divider)
        st.markdown("<div class='faq-suggestions-wrap'>", unsafe_allow_html=True)

        # 3-column fixed grid, up to 9 items
        # We'll render them in rows of 3, using Streamlit columns.
        rows = [suggestions[i:i + 3] for i in range(0, len(suggestions), 3)]
        for r_idx, row in enumerate(rows):
            cols = st.columns(3, gap="small")
            for c_idx, text in enumerate(row):
                with cols[c_idx]:
                    display = text if len(text) <= 64 else text[:61] + "…"
                    key = f"sugg_tile_{r_idx}_{c_idx}_{abs(hash(text)) & 0xFFFF}"
                    if st.button(display, key=key, help=text, use_container_width=True):
                        st.session_state.pending_input = text
                        if hasattr(st, "rerun"):
                            st.rerun()
                        else:
                            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception:
        # never crash the app due to suggestions
        return


# ---- CHAT STREAM (main WhatsApp-style area) --------------------------
def render_chat_stream(
    history: List[tuple],
    assistant_avatar: str = ASSISTANT_AVATAR,
    user_avatar: str = USER_AVATAR,
):
    """Render the WhatsApp-like chat card + messages."""
    # Outer card
    st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)

    # Top bar (avatar + title)
    st.markdown(
        f"""
        <div class="chat-top">
          <div class="chat-top-avatar">
            <img src="{assistant_avatar}" alt="assistant" />
          </div>
          <div>
            <div class="chat-top-title">Support Assistant</div>
            <div class="chat-top-sub">Ask about orders, refunds, login, payments and more.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Messages area
    st.markdown("<div id='chat-container'>", unsafe_allow_html=True)

    if not history:
        st.markdown(
            """
            <div class="welcome">
              <p>👋 <b>Welcome!</b><br/>Ask a question or pick one of the suggestions below.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for role, text, ts in history:
            ts_text = ts.strftime("%H:%M") if isinstance(ts, datetime) else str(ts)
            safe_text = html.escape(str(text)).replace("\n", "<br/>")

            if role == "user":
                st.markdown(
                    f"""
                    <div class="message user">
                      <div class="message-bubble">{safe_text}</div>
                      <div class="avatar"><img src="{user_avatar}" alt="user"/></div>
                    </div>
                    <div class="timestamp">{ts_text}</div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="message assistant">
                      <div class="avatar"><img src="{assistant_avatar}" alt="bot"/></div>
                      <div class="message-bubble">{safe_text}</div>
                    </div>
                    <div class="timestamp">{ts_text}</div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)  # close chat-container

    # Auto-scroll
    st.markdown(
        """
        <script>
        setTimeout(function(){
          var el = document.getElementById('chat-container');
          if (el) { el.scrollTop = el.scrollHeight; }
        }, 100);
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Close chat-shell (the rest of the page can render suggestions/input below)
    st.markdown("</div>", unsafe_allow_html=True)  # close .chat-shell


# ---- RIGHT COLUMN INFO -----------------------------------------------
def render_quick_help():
    """Right-side info panel content (used in main_col2 in app.py)."""
    st.markdown("### 💡 About This App")
    st.markdown(
        """
        **Support Assistant** helps you with:

        - ✅ FAQ answers — quick responses
        - 🎤 Voice input — speak naturally
        - 💬 Chat history — revisit previous questions
        - ⚡ Fast responses from your internal knowledge base
        """
    )
