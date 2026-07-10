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
    """

    # ── Guard: don't show on login screen ─────────────────────────
    if not show:
        return

    # ── Session state ──────────────────────────────────────────────
    if "chat_open"     not in st.session_state: st.session_state.chat_open     = False
    if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

    # ── Read toggle signal from query params ───────────────────────
    params = st.query_params
    if params.get("chat_toggle") == "1":
        st.session_state.chat_open = not st.session_state.chat_open
        # Clear the param to prevent toggling again on rerun
        st.query_params.clear()
        st.rerun()

    is_open       = st.session_state.chat_open
    messages_html = _build_messages_html(st.session_state.chat_messages)
    
    # Determine display states
    fab_style = "display: none;" if is_open else "display: flex;"
    win_style = "display: flex;" if is_open else "display: none;"

    # ── Inject CSS and HTML ────────────────────────────────────────
    st.markdown(f"""
    <style>
    /* ── FAB ── */
    #agri-fab {{
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 999999 !important;
        width: 58px !important;
        height: 58px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        {fab_style}
        align-items: center !important;
        justify-content: center !important;
        font-size: 26px !important;
        line-height: 1 !important;
        cursor: pointer !important;
        box-shadow: 0 6px 22px rgba(78,84,200,.65) !important;
        border: none !important;
        color: white !important;
        transition: transform .2s, box-shadow .2s !important;
        user-select: none !important;
    }}
    #agri-fab:hover {{ 
        transform: scale(1.1) !important; 
        box-shadow: 0 10px 30px rgba(78,84,200,.85) !important; 
    }}

    /* ── Chat window ── */
    #agri-chat-win {{
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 999998 !important;
        width: 348px !important;
        height: 560px !important;
        border-radius: 20px !important;
        background: #1a1b2e !important;
        box-shadow: 0 20px 60px rgba(0,0,0,.6) !important;
        border: 1px solid rgba(255,255,255,.09) !important;
        {win_style}
        flex-direction: column !important;
        overflow: hidden !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}

    /* header */
    #agri-header {{
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        padding: 13px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        flex-shrink: 0 !important;
        color: white !important;
    }}
    #agri-header-left {{ 
        display: flex !important; 
        align-items: center !important; 
        gap: 10px !important; 
    }}
    .agri-avatar {{
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: rgba(255,255,255,.22) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
    }}
    .agri-title  {{ 
        font-size: 14px !important; 
        font-weight: 700 !important; 
        margin: 0 !important; 
        line-height: 1.3 !important; 
    }}
    .agri-status {{ 
        font-size: 11px !important; 
        opacity: .82 !important; 
        margin: 0 !important; 
    }}
    .dot-g       {{ color: #7bffb2 !important; }}
    #agri-close-btn {{
        background: rgba(255,255,255,.18) !important;
        border: none !important;
        color: white !important;
        font-size: 15px !important;
        width: 28px !important;
        height: 28px !important;
        border-radius: 50% !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        transition: background .15s !important;
        line-height: 1 !important;
    }}
    #agri-close-btn:hover {{ background: rgba(255,255,255,.36) !important; }}

    /* messages */
    #agri-messages {{
        flex: 1 !important;
        overflow-y: auto !important;
        padding: 14px 12px 8px 12px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        scroll-behavior: smooth !important;
        scrollbar-width: thin !important;
        scrollbar-color: #3a3b55 transparent !important;
        padding-bottom: 60px !important;
    }}
    #agri-messages::-webkit-scrollbar {{ width: 4px !important; }}
    #agri-messages::-webkit-scrollbar-thumb {{ 
        background: #3a3b55 !important; 
        border-radius: 4px !important; 
    }}

    /* bubbles */
    .bubble {{
        max-width: 88% !important;
        padding: 9px 13px !important;
        border-radius: 16px !important;
        font-size: 13px !important;
        line-height: 1.58 !important;
        word-wrap: break-word !important;
    }}
    .bubble strong {{ font-weight: 700 !important; }}
    .bubble em     {{ font-style: italic !important; }}
    .bubble code {{
        background: rgba(255,255,255,.13) !important;
        padding: 1px 5px !important;
        border-radius: 4px !important;
        font-size: 12px !important;
        font-family: monospace !important;
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
    
    /* ── Hide Streamlit's default chat input when not open ── */
    [data-testid="stChatInput"] {{
        display: {'block' if is_open else 'none'} !important;
        position: fixed !important;
        bottom: 64px !important;
        right: 28px !important;
        width: 292px !important;
        z-index: 999997 !important;
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
    </style>

    <!-- ── FAB ── -->
    <div id="agri-fab" onclick="agriToggle()" title="Open AI Assistant">&#128172;</div>

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

    /* Toggle open/close by setting a query param */
    function agriToggle() {{
        var url = new URL(window.location.href);
        // Toggle the param - if it exists remove it, otherwise set it
        if (url.searchParams.has('chat_toggle')) {{
            url.searchParams.delete('chat_toggle');
        }} else {{
            url.searchParams.set('chat_toggle', '1');
        }}
        window.location.href = url.toString();
    }}
    
    /* Ensure the FAB is clickable after Streamlit rerenders */
    document.addEventListener('DOMContentLoaded', function() {{
        var fab = document.getElementById('agri-fab');
        if (fab) {{
            fab.style.cursor = 'pointer';
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

    # ── Chat input (always rendered, CSS shows/hides it) ──────────
    prompt = st.chat_input(
        "Ask about inventory, orders, pricing…",
        key="agri_chat_input"
    )

    # ── Handle submitted message ───────────────────────────────────
    if prompt and prompt.strip() and is_open:
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
                reply = f"⚠️ Connection error: {e}"
        else:
            reply = "⚠️ Groq API key not configured. Add GROQ_API_KEY to secrets.toml."

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()
