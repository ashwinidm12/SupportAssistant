# ui_components.py
import streamlit as st
import html
from datetime import datetime
from typing import Any

# Default avatars
ASSISTANT_AVATAR = "https://img.icons8.com/color/48/000000/robot-2.png"
USER_AVATAR = "https://img.icons8.com/fluency/48/000000/user-male-circle.png"


def render_css():
    """Clean, modern CSS with ChatGPT-like compact pill input (updated per request)"""
    st.markdown(
        """
    <style>
    /* Clean modern design */
    .main {
        padding-top: 1rem;
    }
    
    /* Header with title and avatar */
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background: white;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 0;
    }
    
    .app-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0b73ff, #0056d6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    
    .app-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin: 0;
    }
    
    /* Chat container */
    #chat-container {
        max-width: 100%;
        padding: 16px 20px;
        min-height: 400px;
        max-height: 60vh;
        overflow-y: auto;
    }
    
    /* Message bubbles */
    .message {
        display: flex;
        margin-bottom: 16px;
        align-items: flex-start;
        gap: 12px;
    }
    
    .message.user {
        flex-direction: row-reverse;
    }
    
    .message-bubble {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 18px;
        word-wrap: break-word;
        line-height: 1.4;
        font-size: 15px;
    }
    
    .message.user .message-bubble {
        background: #0b73ff;
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .message.assistant .message-bubble {
        background: #f3f4f6;
        color: #1f2937;
        border-bottom-left-radius: 4px;
    }
    
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .timestamp {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 4px;
        text-align: right;
    }
    
    .message.user .timestamp {
        text-align: left;
    }
    
    /* Welcome message */
    .welcome {
        text-align: center;
        color: #6b7280;
        padding: 30px 20px;
        font-size: 16px;
    }
    
    /* FAQ Suggestions */
    .faq-suggestions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 8px 0;
        padding: 0 20px;
    }
    
    .faq-chip {
        background: rgba(11, 115, 255, 0.08);
        color: #0b73ff;
        padding: 8px 14px;
        border-radius: 20px;
        border: 1px solid rgba(11, 115, 255, 0.2);
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .faq-chip:hover {
        background: rgba(11, 115, 255, 0.15);
        transform: translateY(-2px);
    }

    /* --- Chat input / control styles (ChatGPT-like compact pill) --- */
    .whatsapp-input-wrapper {
      position: fixed;
      bottom: 16px;
      left: 0;
      right: 0;
      padding: 0 16px;
      z-index: 1000;
      pointer-events: none; /* outer wrapper should not intercept pointer events */
    }

    #whatsapp-input-container {
      pointer-events: auto;
      max-width: 980px;
      margin: 0 auto;
      display: flex;
      align-items: flex-end;
      gap: 8px;
      background: #ffffff;
      border-radius: 20px;
      padding: 8px 12px;
      border: 1px solid #e0e0e0;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    }

    /* left + upload button */
    .input-plus {
      width: 36px;
      height: 36px;
      min-width: 36px;
      border-radius: 10px;
      background: transparent;
      display:flex;
      align-items:center;
      justify-content:center;
      color: #0f172a;
      font-weight:700;
      cursor:pointer;
      border: 1px solid rgba(15,23,42,0.04);
    }

    /* message input (we style Streamlit's textarea via selectors below) */
    .stTextArea > div > div > textarea,
    .custom-chat-input {
      background: transparent;
      border: none;
      padding: 8px 10px;
      font-size: 15px;
      color: #0f172a;
      resize: none;
      line-height: 1.35;
      max-height: calc(1.35em * 4 + 24px); /* 4 lines max + padding */
      min-height: 36px;
      overflow-y: auto;
      width: 100%;
    }

    /* placeholder styling */
    .stTextArea > div > div > textarea::placeholder {
      color: #94a3b8;
    }

    /* mic button (small, to the left of send) */
    .mic-compact {
      width: 36px;
      height: 36px;
      min-width: 36px;
      border-radius: 999px;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      background: transparent;
      border: 1px solid rgba(15,23,42,0.04);
      cursor: pointer;
      color: #0f172a;
      font-size: 16px;
    }

    /* small thumbnails bar above input (compact) */
    .upload-thumbs {
      display:flex;
      gap:8px;
      align-items:center;
      padding: 8px 16px 0 16px;
      max-width: 980px;
      margin: 0 auto;
    }
    .upload-thumb {
      width:48px;
      height:48px;
      border-radius:8px;
      object-fit:cover;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      border: 1px solid rgba(0,0,0,0.04);
    }

    /* send button: round black with white up-arrow icon */
    .send-circle {
      width: 44px;
      height: 44px;
      min-width: 44px;
      border-radius: 999px;
      background: #0f172a;
      color: #ffffff;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      border: none;
      cursor: pointer;
      box-shadow: 0 6px 14px rgba(15,23,42,0.18);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      font-size: 16px;
    }

    /* hover effect */
    .send-circle:hover {
      transform: scale(1.06);
      box-shadow: 0 10px 24px rgba(15,23,42,0.22);
    }

    /* compact spacing for the input row itself */
    #whatsapp-input-container .stMarkdown {
      margin: 0;
    }

    /* reduce overall bottom container padding to keep interface compact */
    .main .block-container {
      padding-bottom: 80px !important;
      padding-top: 8px !important;
    }

    /* ChatGPT-like input container (rounded pill) - alternate rules for Streamlit TextInput */
    .stTextInput > div > div {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        padding: 10px 12px !important;
        font-size: 15px !important;
        width: 100% !important;
        color: #0f172a !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
    }

    .stTextInput > div > div > input:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    .input-plus {
        width: 36px;
        height: 36px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        color: #0f172a;
        font-size: 20px;
        cursor: pointer;
        border: 1px solid rgba(15,23,42,0.04);
    }

    .mic-compact {
        width: 36px;
        height: 36px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        color: #0f172a;
        font-size: 18px;
        cursor: pointer;
        border: 1px solid rgba(15,23,42,0.04);
    }

    /* Send button styling (fallback) */
    button[kind="primary"] {
        background: linear-gradient(90deg, #0b73ff, #0056d6) !important;
        border-radius: 12px !important;
        width: 56px !important;
        height: 36px !important;
        min-height: 36px !important;
        padding: 6px 10px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 6px 12px rgba(11, 115, 255, 0.18) !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 24px rgba(11, 115, 255, 0.22) !important;
    }

    /* Hide Streamlit elements */
    .stApp > header {
        visibility: hidden;
        height: 0;
    }
    
    /* Remove extra padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 100px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header(title: str = "Support Assistant", avatar_url: str | None = None):
    """Render header with title and avatar"""
    if avatar_url is None:
        avatar_url = ASSISTANT_AVATAR

    st.markdown(
        f"""
    <div class="app-header">
        <div class="app-avatar">🤖</div>
        <div>
            <div class="app-title">{html.escape(title)}</div>
            <div class="app-subtitle">AI-powered support assistant</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar_chat_history(history: list[tuple[str, str, Any]]):
    """Sidebar with chat history (history is list of tuples (role, text, timestamp))"""
    with st.sidebar:
        st.markdown("### 💬 Chat History")

        if not history:
            st.info("No conversation history yet.")
        else:
            user_questions: list[tuple[str, Any]] = []
            seen = set()

            # reverse iterate: newest first
            for role, text, ts in reversed(history):
                if role == "user" and isinstance(text, str) and text.strip():
                    text_lower = text.strip().lower()
                    if text_lower not in seen and len(text.strip()) > 3:
                        seen.add(text_lower)
                        user_questions.append((text.strip(), ts))
                        if len(user_questions) >= 15:
                            break

            if user_questions:
                for i, (question, ts) in enumerate(user_questions):
                    label = f"📌 {question[:50]}{'...' if len(question) > 50 else ''}"
                    if st.button(label, key=f"hist_{i}", use_container_width=True):
                        st.session_state.pending_input = question
                        # Streamlit 1.18+ supports st.experimental_rerun; .rerun was older.
                        try:
                            # prefer st.experimental_rerun (works reliably)
                            st.experimental_rerun()
                        except Exception:
                            # fallback to older alias (if available)
                            if hasattr(st, "rerun"):
                                st.rerun()
            else:
                st.info("No questions in history.")


def render_quick_help():
    """Render quick help/objectives in right sidebar"""
    st.markdown("### 💡 About This App")
    st.markdown(
        """
    **Support Assistant** helps you with:
    
    - ✅ **FAQ Answers** - Quick responses to common questions
    - 🎤 **Voice Input** - Speak your questions naturally
    - 💬 **Chat History** - Access your previous queries
    - ⚡ **Fast Responses** - Instant answers from our knowledge base
    - 🔒 **Secure** - Your data is handled securely
    
    **How to use:**
    1. Type your question or click a suggestion
    2. Use 🎤 to record voice messages
    3. Click ➤ to send
    4. View history in the left sidebar
    """
    )


def render_faq_suggestions(agent):
    """Render FAQ suggestion chips (robustly handle different agent signatures)"""
    try:
        # some agent implementations expect build_suggestions(limit=..) or build_suggestions(top_n=..)
        try:
            suggestions = agent.build_suggestions(limit=8)  # preferred if implemented
        except TypeError:
            try:
                suggestions = agent.build_suggestions(top_n=8)
            except TypeError:
                suggestions = agent.build_suggestions()
        if suggestions:
            st.markdown("<div class='faq-suggestions'>", unsafe_allow_html=True)
            cols = st.columns(min(len(suggestions), 4))
            for i, s in enumerate(suggestions[:8]):
                col_idx = i % 4
                with cols[col_idx]:
                    if st.button(s, key=f"suggestion_{i}", use_container_width=True):
                        st.session_state.pending_input = s
                        try:
                            st.experimental_rerun()
                        except Exception:
                            if hasattr(st, "rerun"):
                                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        # gracefully ignore UI failures (we don't want the whole app to crash)
        pass


def render_chat_stream(history: list[tuple[str, str, Any]], assistant_avatar: str = ASSISTANT_AVATAR, user_avatar: str = USER_AVATAR):
    """Render clean chat messages"""
    st.markdown("<div id='chat-container'>", unsafe_allow_html=True)

    if not history:
        st.markdown(
            """
        <div class='welcome'>
            <h2 style='color:#1f2937;margin-bottom:8px;'>👋 Welcome!</h2>
            <p>Ask me anything or use the 🎤 button to speak.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        for role, text, ts in history:
            ts_text = ts.strftime("%H:%M") if isinstance(ts, datetime) else str(ts)
            safe_text = html.escape(text).replace("\n", "<br/>")

            if role == "user":
                st.markdown(
                    f"""
                <div class='message user'>
                    <div class='message-bubble'>{safe_text}</div>
                    <img class='avatar' src='{user_avatar}' />
                </div>
                <div class='timestamp'>{ts_text}</div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class='message assistant'>
                    <img class='avatar' src='{assistant_avatar}' />
                    <div class='message-bubble'>{safe_text}</div>
                </div>
                <div class='timestamp'>{ts_text}</div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-scroll
    st.markdown(
        """
    <script>
        setTimeout(function() {
            var el = document.getElementById('chat-container');
            if (el) el.scrollTop = el.scrollHeight;
        }, 100);
    </script>
    """,
        unsafe_allow_html=True,
    )
