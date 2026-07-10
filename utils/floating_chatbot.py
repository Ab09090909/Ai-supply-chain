import os
import re
import streamlit as st
from groq import Groq


def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


@st.cache_resource
def init_groq_client():
    return get_groq_client()


def _md_to_html(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"(?m)^(\d+\.\s)", r"<br>\1", text)
    text = re.sub(r"(?m)^[\*\-]\s+", "<br>• ", text)
    text = re.sub(r"\n{2,}", "<br><br>", text)
    text = text.replace("\n", "<br>")
    text = re.sub(r"^(<br>)+", "", text)
    return text


def _build_messages_html(messages: list) -> str:
    if not messages:
        return (
            '<div class="bubble bot-bubble">'
            "&#128075; Hello! I&#39;m your AgriTech AI Assistant.<br>"
            "Ask me anything about orders, inventory, pricing, or analytics."
            "</div>"
        )
    parts = []
    for msg in messages:
        content = _md_to_html(msg["content"])
        css = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        parts.append(f'<div class="bubble {css}">{content}</div>')
    return "\n".join(parts)


def _get_ai_reply(user_context: str) -> str:
    client = init_groq_client()
    if not client:
        return "⚠️ Groq API key not configured. Add GROQ_API_KEY to secrets.toml."

    try:
        system_msg = {
            "role": "system",
            "content": (
                "You are the AI Supply Chain Assistant for the Ethiopian AgriTech platform. "
                "Help Producers, Merchants, Customers, and Admins. Be professional and concise.\n"
                "Formatting rules: use **bold** for key terms, numbered lists for steps, "
                "bullet points for options. Do NOT use markdown headers (#, ##).\n\n"
                f"CURRENT USER CONTEXT:\n{user_context}"
            ),
        }
        api_msgs = [system_msg] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_messages[-12:]
        ]
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_msgs,
            temperature=0.7,
            max_tokens=1024,
            stream=False,
        )
        return resp.choices[0].message.content or "Sorry, no response generated."
    except Exception as e:
        return f"⚠️ Connection error: {e}"


def render_floating_chatbot(user_context: str = "", show: bool = True):
    if not show:
        return

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    is_open = st.session_state.chat_open
    messages_html = _build_messages_html(st.session_state.chat_messages)
    fab_display = "none" if is_open else "flex"
    win_display = "flex" if is_open else "none"

    # ── CSS + floating shell (messages only; input is Streamlit) ──
    st.markdown(
        f"""
    <style>
    #agri-fab {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 999999 !important;
        width: 58px !important;
        height: 58px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        display: {fab_display} !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 28px !important;
        cursor: pointer !important;
        box-shadow: 0 6px 22px rgba(78,84,200,.65) !important;
        border: none !important;
        color: white !important;
        user-select: none !important;
        text-decoration: none !important;
    }}
    #agri-fab:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 10px 30px rgba(78,84,200,.85) !important;
    }}

    #agri-chat-win {{
        position: fixed !important;
        bottom: 90px !important;
        right: 20px !important;
        z-index: 999998 !important;
        width: 360px !important;
        max-height: 520px !important;
        border-radius: 16px !important;
        background: #1a1b2e !important;
        box-shadow: 0 20px 60px rgba(0,0,0,.7) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        display: {win_display} !important;
        flex-direction: column !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}

    #agri-header {{
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        padding: 12px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        color: white !important;
        min-height: 56px !important;
    }}
    #agri-header-left {{ display: flex !important; align-items: center !important; gap: 10px !important; }}
    .agri-avatar {{
        width: 32px !important; height: 32px !important; border-radius: 50% !important;
        background: rgba(255,255,255,.2) !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        font-size: 16px !important;
    }}
    .agri-title {{ font-size: 14px !important; font-weight: 600 !important; margin: 0 !important; }}
    .agri-status {{ font-size: 10px !important; opacity: .8 !important; margin: 0 !important; }}
    .dot-green {{ color: #7bffb2 !important; }}

    #agri-messages {{
        flex: 1 !important;
        overflow-y: auto !important;
        padding: 12px 14px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
        max-height: 340px !important;
        min-height: 200px !important;
        scrollbar-width: thin !important;
        scrollbar-color: #3a3b55 transparent !important;
    }}
    #agri-messages::-webkit-scrollbar {{ width: 4px !important; }}
    #agri-messages::-webkit-scrollbar-thumb {{ background: #3a3b55 !important; border-radius: 4px !important; }}

    .bubble {{
        max-width: 85% !important;
        padding: 8px 12px !important;
        border-radius: 12px !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
        word-wrap: break-word !important;
    }}
    .user-bubble {{
        align-self: flex-end !important;
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        color: white !important;
        border-bottom-right-radius: 4px !important;
    }}
    .bot-bubble {{
        align-self: flex-start !important;
        background: #252640 !important;
        color: #dde0ff !important;
        border-bottom-left-radius: 4px !important;
    }}
    .bubble code {{
        background: rgba(255,255,255,.1) !important;
        padding: 1px 4px !important;
        border-radius: 3px !important;
        font-size: 12px !important;
        font-family: monospace !important;
    }}

    /* Anchor Streamlit controls into the floating window */
    div[data-testid="stVerticalBlock"]:has(> div > #agri-chat-controls) {{
        position: fixed !important;
        bottom: 90px !important;
        right: 20px !important;
        width: 360px !important;
        z-index: 999999 !important;
        display: {"block" if is_open else "none"} !important;
        pointer-events: none !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> div > #agri-chat-controls) * {{
        pointer-events: auto !important;
    }}

    /* Close / clear row sits under header visually */
    #agri-chat-controls {{
        margin-top: 8px !important;
        padding: 0 10px !important;
    }}

    /* Chat input docked to bottom of window */
    div[data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 98px !important;
        right: 28px !important;
        width: 344px !important;
        z-index: 1000000 !important;
        display: {"block" if is_open else "none"} !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        background: #12132a !important;
        color: #dde0ff !important;
        border: 1.5px solid #4e54c8 !important;
        border-radius: 20px !important;
        font-size: 13px !important;
    }}

    /* Invisible FAB streamlit button over the emoji FAB */
    div[data-testid="stVerticalBlock"]:has(> div > #agri-fab-btn) {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        width: 58px !important;
        height: 58px !important;
        z-index: 1000001 !important;
        display: {"none" if is_open else "block"} !important;
    }}
    #agri-fab-btn + div button {{
        width: 58px !important;
        height: 58px !important;
        border-radius: 50% !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }}
    </style>

    <div id="agri-fab">💬</div>

    <div id="agri-chat-win">
        <div id="agri-header">
            <div id="agri-header-left">
                <div class="agri-avatar">🤖</div>
                <div>
                    <p class="agri-title">AgriTech Assistant</p>
                    <p class="agri-status"><span class="dot-green">●</span> Online</p>
                </div>
            </div>
        </div>
        <div id="agri-messages">
            {messages_html}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Streamlit controls (wired to session state) ──
    # Invisible FAB click target
    st.markdown('<div id="agri-fab-btn"></div>', unsafe_allow_html=True)
    if st.button("open", key="fab_open", help="Open chat"):
        st.session_state.chat_open = True
        st.rerun()

    if is_open:
        st.markdown('<div id="agri-chat-controls"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✕ Close", key="chat_close", use_container_width=True):
                st.session_state.chat_open = False
                st.rerun()
        with c2:
            if st.button("🗑 Clear", key="chat_clear", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

        prompt = st.chat_input("Ask about inventory, orders, pricing…", key="agri_chat_input")
        if prompt and prompt.strip():
            st.session_state.chat_messages.append(
                {"role": "user", "content": prompt.strip()}
            )
            reply = _get_ai_reply(user_context)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()
