import os
import streamlit as st
from groq import Groq
from streamlit_float import *

# Initialize the float feature globally
float_init()


def get_groq_client():
    """Initialize Groq client using Streamlit secrets or environment variables."""
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("Groq API Key not found. Please add it to .streamlit/secrets.toml or .env file.")
        return None
    return Groq(api_key=api_key)


@st.cache_resource
def init_groq_client():
    return get_groq_client()


def inject_chatbot_styles():
    """Inject CSS for floating chat widget."""
    st.markdown("""
    <style>
    /* ── FAB Button ── */
    div[data-testid="stButton"] button[kind="secondary"]#open_chat_btn,
    div[data-testid="stButton"] > button {
        all: unset;
    }

    /* Target the open-chat button by key via aria-label workaround */
    .fab-wrapper button {
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%) !important;
        color: white !important;
        font-size: 26px !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 8px 24px rgba(78, 84, 200, 0.55) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        line-height: 1 !important;
        padding: 0 !important;
    }

    .fab-wrapper button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 12px 32px rgba(78, 84, 200, 0.7) !important;
    }

    /* ── Chat Window ── */
    .chat-window {
        width: 360px;
        height: 520px;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 16px 48px rgba(0,0,0,0.18);
        border: 1px solid rgba(0,0,0,0.08);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
    }

    /* ── Header ── */
    .chat-header {
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        flex-shrink: 0;
    }
    .chat-header-left { display: flex; align-items: center; gap: 10px; }
    .chat-avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: rgba(255,255,255,0.22);
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }
    .chat-title  { font-size: 15px; font-weight: 700; margin: 0; line-height: 1.2; }
    .chat-status { font-size: 11px; opacity: 0.82; margin: 0; }
    .online-dot  { color: #7BFFB2; margin-right: 4px; }

    /* ── Messages scroll area ── */
    .chat-scroll {
        flex: 1;
        overflow-y: auto;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        scrollbar-width: thin;
        scrollbar-color: #d0d0d0 transparent;
    }
    .chat-scroll::-webkit-scrollbar { width: 5px; }
    .chat-scroll::-webkit-scrollbar-thumb { background: #d0d0d0; border-radius: 6px; }

    /* ── Individual message bubbles ── */
    .msg-row-user { display: flex; justify-content: flex-end; }
    .msg-row-assistant { display: flex; justify-content: flex-start; }

    .bubble {
        max-width: 82%;
        padding: 9px 13px;
        border-radius: 16px;
        font-size: 13.5px;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .bubble-user {
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        color: white;
        border-bottom-right-radius: 4px;
    }
    .bubble-assistant {
        background: #f3f4f8;
        color: #1a1a2e;
        border-bottom-left-radius: 4px;
    }

    /* ── Welcome message ── */
    .welcome-bubble {
        background: #eef0ff;
        border: 1px solid #c7caff;
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 13px;
        color: #3a3d8f;
        margin-bottom: 4px;
    }

    /* ── Input area ── */
    .chat-input-wrapper {
        padding: 10px 12px;
        border-top: 1px solid #f0f0f0;
        background: #fafafa;
        flex-shrink: 0;
    }

    /* Make Streamlit chat_input fit inside the widget */
    .chat-input-wrapper .stChatInput {
        margin: 0 !important;
    }
    .chat-input-wrapper .stChatInput > div {
        border-radius: 12px !important;
        border: 1.5px solid #d0d3ff !important;
        background: white !important;
    }
    .chat-input-wrapper .stChatInput textarea {
        font-size: 13px !important;
    }

    /* ── Close button ── */
    .close-btn button {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 30px !important;
        height: 30px !important;
        font-size: 14px !important;
        padding: 0 !important;
        cursor: pointer !important;
        line-height: 1 !important;
    }
    .close-btn button:hover {
        background: rgba(255,255,255,0.35) !important;
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .chat-window { background: #1e1e2e; border-color: rgba(255,255,255,0.1); }
        .bubble-assistant { background: #2a2a3e; color: #e8e8f0; }
        .chat-input-wrapper { background: #1a1a2e; border-top-color: #2a2a3e; }
    }
    </style>
    """, unsafe_allow_html=True)


def _build_messages_html(messages):
    """Render all chat messages as HTML bubbles for the scroll area."""
    if not messages:
        return '<div class="welcome-bubble">👋 Hello! I\'m your AgriTech AI Assistant. Ask me anything about orders, inventory, pricing, or analytics.</div>'

    html = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if role == "user":
            html += f'<div class="msg-row-user"><div class="bubble bubble-user">{content}</div></div>'
        else:
            html += f'<div class="msg-row-assistant"><div class="bubble bubble-assistant">{content}</div></div>'
    return html


def render_floating_chatbot(user_context: str = ""):
    """Main function to render the floating AI assistant."""

    # ── Session state init ──
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    inject_chatbot_styles()

    # ── Float container ──
    float_container = st.container()
    float_container.float("bottom: 1.5rem; right: 1.5rem; z-index: 9999;")

    with float_container:

        if not st.session_state.chat_open:
            # ── FAB (Floating Action Button) ──
            st.markdown('<div class="fab-wrapper">', unsafe_allow_html=True)
            if st.button("💬", key="open_chat", help="Open AI Assistant"):
                st.session_state.chat_open = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # ── Chat Window ──
            st.markdown('<div class="chat-window">', unsafe_allow_html=True)

            # Header row
            col_title, col_close = st.columns([5, 1])
            with col_title:
                st.markdown("""
                <div class="chat-header">
                    <div class="chat-header-left">
                        <div class="chat-avatar">🤖</div>
                        <div>
                            <p class="chat-title">AgriTech AI Assistant</p>
                            <p class="chat-status"><span class="online-dot">●</span>Online · Powered by Groq</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_close:
                st.markdown('<div class="close-btn" style="padding-top:8px;">', unsafe_allow_html=True)
                if st.button("✕", key="close_chat", help="Close"):
                    st.session_state.chat_open = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Messages: rendered as static HTML so scroll works ──
            messages_html = _build_messages_html(st.session_state.chat_messages)
            # JS auto-scrolls to bottom on each render
            st.markdown(f"""
            <div class="chat-scroll" id="chat-scroll-box">
                {messages_html}
            </div>
            <script>
                const box = document.getElementById('chat-scroll-box');
                if (box) box.scrollTop = box.scrollHeight;
            </script>
            """, unsafe_allow_html=True)

            # ── Input ──
            st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
            prompt = st.chat_input("Ask about inventory, orders, pricing…", key="chat_input")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # end .chat-window

            # ── Handle new message ──
            if prompt:
                st.session_state.chat_messages.append({"role": "user", "content": prompt})

                client = init_groq_client()
                if client:
                    try:
                        system_msg = {
                            "role": "system",
                            "content": (
                                "You are the AI Supply Chain Assistant for the Ethiopian AgriTech platform. "
                                "You help Producers, Merchants, Customers, and Admins. "
                                "Be professional, concise, and proactive.\n\n"
                                f"CURRENT USER REAL-TIME CONTEXT:\n{user_context}\n\n"
                                "Use this data to give personalized, data-driven answers."
                            ),
                        }
                        messages_for_api = [system_msg] + st.session_state.chat_messages[-10:]

                        # Non-streaming call — avoids partial render artifacts inside float
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=messages_for_api,
                            temperature=0.7,
                            max_tokens=1024,
                            stream=False,
                        )
                        reply = response.choices[0].message.content or ""
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

                    except Exception as e:
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": f"⚠️ Error connecting to Groq: {e}"
                        })

                st.rerun()  # single rerun after state is fully updated
