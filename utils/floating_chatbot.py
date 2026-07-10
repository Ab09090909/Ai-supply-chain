import os
import re
import streamlit as st
from groq import Groq

# NOTE: streamlit_float is NOT used here.
# Reason: streamlit_float wraps Streamlit widgets inside a positioned container,
# but Streamlit widgets (st.button, st.chat_input) always render in the main DOM
# flow — they escape the float wrapper, causing the broken layout seen in screenshots.
# Solution: the entire chat UI (FAB + window + messages + input) is rendered as a
# single st.markdown() HTML/CSS/JS block, with position:fixed applied directly.
# Only the invisible open/close state buttons remain as Streamlit widgets, hidden via CSS.


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
    """Convert common LLM markdown to safe inline HTML for bubble display."""
    # Escape HTML first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Numbered list  "1. item"  →  "1. item" with a line break before each
    text = re.sub(r'(?m)^(\d+\.\s)', r'<br>\1', text)
    # Bullet list  "* item" or "- item"
    text = re.sub(r'(?m)^[\*\-]\s+', '<br>• ', text)
    # Paragraph breaks → double <br>
    text = re.sub(r'\n{2,}', '<br><br>', text)
    # Single newlines → <br>
    text = text.replace('\n', '<br>')
    # Strip leading <br> added by list regexes
    text = re.sub(r'^(<br>)+', '', text)
    return text


# ── Build messages HTML ───────────────────────────────────────────────────────

def _build_messages_html(messages: list) -> str:
    if not messages:
        return (
            '<div class="bubble bot-bubble">'
            '👋 Hello! I\'m your AgriTech AI Assistant.<br>'
            'Ask me anything about orders, inventory, pricing, or analytics.'
            '</div>'
        )
    parts = []
    for msg in messages:
        content = _md_to_html(msg["content"])
        if msg["role"] == "user":
            parts.append(f'<div class="bubble user-bubble">{content}</div>')
        else:
            parts.append(f'<div class="bubble bot-bubble">{content}</div>')
    return "\n".join(parts)


# ── Main render function ──────────────────────────────────────────────────────

def render_floating_chatbot(user_context: str = ""):
    """
    Render the floating AI chat widget.

    Architecture
    ────────────
    • FAB + chat window  → single st.markdown() block with position:fixed CSS.
      No Streamlit layout widgets are used inside, so nothing can escape and
      break the page layout.
    • Open / Close state → two tiny hidden st.button() elements that trigger
      st.rerun() when clicked. JS onclick on the HTML buttons submits a hidden
      Streamlit form to toggle state without a full page reload visual glitch.
    • Chat input         → st.chat_input() rendered once, globally (not inside
      any float container). It is then repositioned via CSS to overlap the
      widget footer area.
    • Messages + scroll  → pure HTML <div> with overflow-y:auto + JS scrollTop.
    • Markdown rendering → custom _md_to_html() so **bold**, lists etc. display
      correctly instead of showing raw asterisks.
    """

    # ── session state ──────────────────────────────────────────────
    if "chat_open"     not in st.session_state: st.session_state.chat_open     = False
    if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

    is_open       = st.session_state.chat_open
    messages_html = _build_messages_html(st.session_state.chat_messages)
    win_display   = "flex"   if is_open else "none"
    fab_display   = "none"   if is_open else "flex"

    # ── inject CSS + full HTML widget ─────────────────────────────
    st.markdown(f"""
    <style>
    /* ── Reset Streamlit interference ── */
    [data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 68px !important;
        right: 28px !important;
        width: 296px !important;
        z-index: 100001 !important;
        display: {"block" if is_open else "none"} !important;
    }}
    [data-testid="stChatInput"] > div {{
        border-radius: 12px !important;
        border: 1.5px solid #4e54c8 !important;
        background: #14152a !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: #dde0ff !important;
        font-size: 13px !important;
        background: transparent !important;
    }}
    [data-testid="stChatInput"] button {{ color: #8f94fb !important; }}

    /* hide the tiny open/close state-buttons */
    button[data-testid="baseButton-secondary"] {{
        visibility: hidden !important;
        position: absolute !important;
        width: 0 !important; height: 0 !important;
        padding: 0 !important; margin: 0 !important;
        border: none !important; overflow: hidden !important;
    }}

    /* ── FAB ── */
    #agri-fab {{
        position: fixed;
        bottom: 24px; right: 24px;
        z-index: 100000;
        width: 58px; height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        display: {fab_display};
        align-items: center; justify-content: center;
        font-size: 26px;
        cursor: pointer;
        box-shadow: 0 6px 22px rgba(78,84,200,.6);
        border: none; color: white;
        transition: transform .2s, box-shadow .2s;
        user-select: none;
    }}
    #agri-fab:hover {{ transform: scale(1.1); box-shadow: 0 10px 30px rgba(78,84,200,.8); }}

    /* ── Chat window ── */
    #agri-chat-win {{
        position: fixed;
        bottom: 20px; right: 20px;
        z-index: 99999;
        width: 340px;
        /* 500px body + 56px header + 52px input footer */
        height: 608px;
        border-radius: 20px;
        background: #1a1b2e;
        box-shadow: 0 20px 60px rgba(0,0,0,.55);
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
        background: rgba(255,255,255,.2);
        display: flex; align-items: center; justify-content: center; font-size: 18px;
    }}
    .agri-title  {{ font-size: 14px; font-weight: 700; margin: 0; line-height: 1.3; }}
    .agri-status {{ font-size: 11px; opacity: .82; margin: 0; }}
    .dot-g       {{ color: #7bffb2; }}
    #agri-close-html {{
        background: rgba(255,255,255,.18); border: none; color: white;
        font-size: 15px; width: 28px; height: 28px; border-radius: 50%;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; transition: background .15s;
    }}
    #agri-close-html:hover {{ background: rgba(255,255,255,.35); }}

    /* messages */
    #agri-messages {{
        flex: 1;
        overflow-y: auto;
        padding: 14px 12px;
        display: flex; flex-direction: column; gap: 8px;
        scroll-behavior: smooth;
        scrollbar-width: thin; scrollbar-color: #3a3b55 transparent;
    }}
    #agri-messages::-webkit-scrollbar {{ width: 4px; }}
    #agri-messages::-webkit-scrollbar-thumb {{ background: #3a3b55; border-radius: 4px; }}

    /* bubbles */
    .bubble {{
        max-width: 88%; padding: 9px 13px; border-radius: 16px;
        font-size: 13px; line-height: 1.58; word-wrap: break-word;
    }}
    .bubble strong {{ font-weight: 700; }}
    .bubble code {{
        background: rgba(255,255,255,.13); padding: 1px 4px;
        border-radius: 4px; font-size: 12px;
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

    /* footer spacer so last bubble isn't hidden behind the fixed input */
    #agri-footer-spacer {{ height: 52px; flex-shrink: 0; }}
    </style>

    <!-- FAB -->
    <button id="agri-fab" onclick="agriFabClick()" title="Open AI Assistant">💬</button>

    <!-- Chat window -->
    <div id="agri-chat-win">

      <!-- Header -->
      <div id="agri-header">
        <div id="agri-header-left">
          <div class="agri-avatar">🤖</div>
          <div>
            <p class="agri-title">AgriTech AI Assistant</p>
            <p class="agri-status"><span class="dot-g">●</span> Online · Powered by Groq</p>
          </div>
        </div>
        <button id="agri-close-html" onclick="agriCloseClick()" title="Close">✕</button>
      </div>

      <!-- Messages -->
      <div id="agri-messages">
        {messages_html}
      </div>

      <!-- Spacer so chat_input doesn't cover last bubble -->
      <div id="agri-footer-spacer"></div>

    </div>

    <script>
    // Auto-scroll messages to bottom
    (function() {{
      var box = document.getElementById('agri-messages');
      if (box) box.scrollTop = box.scrollHeight;
    }})();

    // FAB click → click the hidden Streamlit "open" button
    function agriFabClick() {{
      var btn = window.parent.document.querySelector('button[data-testid="baseButton-secondary"][aria-label="__agri_open__"]');
      if (btn) btn.click();
    }}
    // Close click → click the hidden Streamlit "close" button
    function agriCloseClick() {{
      var btn = window.parent.document.querySelector('button[data-testid="baseButton-secondary"][aria-label="__agri_close__"]');
      if (btn) btn.click();
    }}
    </script>
    """, unsafe_allow_html=True)

    # ── Hidden state-toggle buttons (aria-label used as selector by JS) ───────
    col, _ = st.columns([1, 50])
    with col:
        if st.button("o", key="_agri_open_btn",  help="__agri_open__"):
            st.session_state.chat_open = True
            st.rerun()
        if st.button("c", key="_agri_close_btn", help="__agri_close__"):
            st.session_state.chat_open = False
            st.rerun()

    # ── Chat input — always rendered globally, shown/hidden via CSS ───────────
    prompt = st.chat_input(
        "Ask about inventory, orders, pricing…",
        key="agri_chat_input"
    )

    # ── Handle submitted message ──────────────────────────────────────────────
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
                        "Format rules: use **bold** for key terms, numbered lists for steps, "
                        "plain paragraphs otherwise. Do NOT use markdown headers (#, ##).\n\n"
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
