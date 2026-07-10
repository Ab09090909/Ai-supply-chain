import os
import re
import streamlit as st
from groq import Groq


# ── Groq client ───────────────────────────────────────────────────────────────

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


@st.cache_resource
def init_groq_client():
    return get_groq_client()


# ── Markdown → safe HTML ──────────────────────────────────────────────────────

def _md_to_html(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    text = re.sub(r'`(.+?)`',       r'<code>\1</code>',     text)
    text = re.sub(r'(?m)^(\d+\.\s)', r'<br>\1', text)
    text = re.sub(r'(?m)^[\*\-]\s+', '<br>• ',  text)
    text = re.sub(r'\n{2,}', '<br><br>', text)
    text = text.replace('\n', '<br>')
    text = re.sub(r'^(<br>)+', '', text)
    return text


def _build_messages_html(messages: list) -> str:
    if not messages:
        return (
            '<div class="bubble bot-bubble">'
            '&#128075; Hello! I\'m your AgriTech AI Assistant.<br>'
            'Ask me anything about orders, inventory, pricing, or analytics.'
            '</div>'
        )
    parts = []
    for msg in messages:
        content = _md_to_html(msg["content"])
        css = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        parts.append(f'<div class="bubble {css}">{content}</div>')
    return "\n".join(parts)


# ── Main render function ──────────────────────────────────────────────────────

def render_floating_chatbot(user_context: str = "", show: bool = True):
    """
    Render the floating AI chat widget.

    Parameters
    ----------
    user_context : str
        Real-time DB context string injected into the system prompt.
    show : bool
        Pass False on the login / signup page to hide the widget entirely.
        Example in app.py / router:
            from chatbot_widget import render_floating_chatbot
            is_logged_in = st.session_state.get("user") is not None
            render_floating_chatbot(user_context=ctx, show=is_logged_in)
    """

    # ── Guard: don't show on login screen ─────────────────────────
    if not show:
        return

    # ── Session state ──────────────────────────────────────────────
    if "chat_open"     not in st.session_state: st.session_state.chat_open     = False
    if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

    # ── Read toggle signal from query params ───────────────────────
    # JS sets ?chat_toggle=1 in the URL; we detect it here, flip state,
    # clear the param, and rerun — no hidden buttons needed at all.
    params = st.query_params
    if params.get("chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.query_params.clear()
        st.rerun()

    is_open       = st.session_state.chat_open
    messages_html = _build_messages_html(st.session_state.chat_messages)
    win_display   = "flex" if is_open else "none"
    fab_display   = "none" if is_open else "flex"
    input_display = "block" if is_open else "none"

    # ── CSS + HTML (single markdown block, position:fixed everywhere) ─
    st.markdown(f"""
    <style>
    /* ── Chat input repositioned to widget footer ── */
    [data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 64px !important;
        right: 28px !important;
        width: 292px !important;
        z-index: 100001 !important;
        display: {input_display} !important;
        margin: 0 !important;
    }}
    [data-testid="stChatInput"] > div {{
        border-radius: 12px !important;
        border: 1.5px solid #4e54c8 !important;
        background: #12132a !important;
        box-shadow: none !important;
        margin: 0 !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: #dde0ff !important;
        font-size: 13px !important;
        background: transparent !important;
    }}
    [data-testid="stChatInput"] button {{ color: #8f94fb !important; }}

    /* ── FAB ── */
    #agri-fab {{
        position: fixed;
        bottom: 24px; right: 24px;
        z-index: 100002;
        width: 58px; height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        display: {fab_display};
        align-items: center; justify-content: center;
        font-size: 26px; line-height: 1;
        cursor: pointer;
        box-shadow: 0 6px 22px rgba(78,84,200,.65);
        border: none; color: white;
        transition: transform .2s, box-shadow .2s;
        user-select: none;
    }}
    #agri-fab:hover {{ transform: scale(1.1); box-shadow: 0 10px 30px rgba(78,84,200,.85); }}

    /* ── Chat window ── */
    #agri-chat-win {{
        position: fixed;
        bottom: 20px; right: 20px;
        z-index: 100000;
        width: 348px;
        height: 560px;
        border-radius: 20px;
        background: #1a1b2e;
        box-shadow: 0 20px 60px rgba(0,0,0,.6);
        border: 1px solid rgba(255,255,255,.09);
        display: {win_display};
        flex-direction: column;
        overflow: hidden;
        font-family: 'Inter', system-ui, sans-serif;
    }}

    /* header */
    #agri-header {{
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        padding: 13px 16px;
        display: flex; align-items: center; justify-content: space-between;
        flex-shrink: 0; color: white;
    }}
    #agri-header-left {{ display: flex; align-items: center; gap: 10px; }}
    .agri-avatar {{
        width: 36px; height: 36px; border-radius: 50%;
        background: rgba(255,255,255,.22);
        display: flex; align-items: center; justify-content: center; font-size: 18px;
    }}
    .agri-title  {{ font-size: 14px; font-weight: 700; margin: 0; line-height: 1.3; }}
    .agri-status {{ font-size: 11px; opacity: .82; margin: 0; }}
    .dot-g       {{ color: #7bffb2; }}
    #agri-close-btn {{
        background: rgba(255,255,255,.18); border: none; color: white;
        font-size: 15px; width: 28px; height: 28px; border-radius: 50%;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; transition: background .15s; line-height: 1;
    }}
    #agri-close-btn:hover {{ background: rgba(255,255,255,.36); }}

    /* messages */
    #agri-messages {{
        flex: 1;
        overflow-y: auto;
        padding: 14px 12px 8px 12px;
        display: flex; flex-direction: column; gap: 8px;
        scroll-behavior: smooth;
        scrollbar-width: thin; scrollbar-color: #3a3b55 transparent;
        /* leave room for the fixed chat_input at the bottom */
        padding-bottom: 60px;
    }}
    #agri-messages::-webkit-scrollbar {{ width: 4px; }}
    #agri-messages::-webkit-scrollbar-thumb {{ background: #3a3b55; border-radius: 4px; }}

    /* bubbles */
    .bubble {{
        max-width: 88%; padding: 9px 13px; border-radius: 16px;
        font-size: 13px; line-height: 1.58; word-wrap: break-word;
    }}
    .bubble strong {{ font-weight: 700; }}
    .bubble em     {{ font-style: italic; }}
    .bubble code {{
        background: rgba(255,255,255,.13); padding: 1px 5px;
        border-radius: 4px; font-size: 12px; font-family: monospace;
    }}
    .user-bubble {{
        align-self: flex-end;
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        color: white; border-bottom-right-radius: 4px;
    }}
    .bot-bubble {{
        align-self: flex-start;
        background: #252640; color: #dde0ff; border-bottom-left-radius: 4px;
    }}
    </style>

    <!-- ── FAB ── -->
    <button id="agri-fab" onclick="agriToggle()" title="Open AI Assistant">&#128172;</button>

    <!-- ── Chat window ── -->
    <div id="agri-chat-win">
      <div id="agri-header">
        <div id="agri-header-left">
          <div class="agri-avatar">&#129302;</div>
          <div>
            <p class="agri-title">AgriTech AI Assistant</p>
            <p class="agri-status"><span class="dot-g">&#9679;</span> Online &middot; Powered by Groq</p>
          </div>
        </div>
        <button id="agri-close-btn" onclick="agriToggle()" title="Close">&#10005;</button>
      </div>

      <div id="agri-messages">
        {messages_html}
      </div>
    </div>

    <script>
    /* Scroll messages to bottom on every render */
    (function() {{
      var b = document.getElementById('agri-messages');
      if (b) b.scrollTop = b.scrollHeight;
    }})();

    /* Toggle open/close by setting a query param — Streamlit detects it,
       flips chat_open in session_state, clears the param, and reruns.
       This avoids ALL hidden-button selector issues. */
    function agriToggle() {{
      var url = new URL(window.location.href);
      url.searchParams.set('chat_toggle', '1');
      window.location.href = url.toString();
    }}
    </script>
    """, unsafe_allow_html=True)

    # ── Chat input (always rendered, CSS shows/hides it) ──────────
    prompt = st.chat_input(
        "Ask about inventory, orders, pricing\u2026",
        key="agri_chat_input"
    )

    # ── Handle submitted message ───────────────────────────────────
    if prompt and prompt.strip():
        st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})

        client = init_groq_client()
        if client:
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
                reply = resp.choices[0].message.content or "Sorry, no response generated."
            except Exception as e:
                reply = f"&#9888;&#65039; Connection error: {e}"
        else:
            reply = "&#9888;&#65039; Groq API key not configured. Add GROQ_API_KEY to secrets.toml."

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()
