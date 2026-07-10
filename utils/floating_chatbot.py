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
    """
    # ── Guard: don't show on login screen ─────────────────────────
    if not show:
        return

    # ── Session state ──────────────────────────────────────────────
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # ── Handle toggle via query param ────────────────────────────
    # Check if toggle was requested
    params = st.query_params
    if params.get("chat_toggle") == "1":
        st.session_state.chat_open = not st.session_state.chat_open
        st.query_params.clear()
        st.rerun()

    is_open = st.session_state.chat_open
    messages_html = _build_messages_html(st.session_state.chat_messages)
    
    # Determine display states
    fab_display = "none" if is_open else "flex"
    win_display = "flex" if is_open else "none"
    input_display = "block" if is_open else "none"

    # ── Inject CSS and HTML ────────────────────────────────────────
    st.markdown(f"""
    <style>
    /* ── FAB Button ── */
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
        line-height: 1 !important;
        cursor: pointer !important;
        box-shadow: 0 6px 22px rgba(78,84,200,.65) !important;
        border: none !important;
        color: white !important;
        transition: all 0.3s ease !important;
        user-select: none !important;
        padding: 0 !important;
        text-decoration: none !important;
    }}
    #agri-fab:hover {{ 
        transform: scale(1.1) !important; 
        box-shadow: 0 10px 30px rgba(78,84,200,.85) !important; 
    }}

    /* ── Chat Window ── */
    #agri-chat-win {{
        position: fixed !important;
        bottom: 90px !important;
        right: 20px !important;
        z-index: 999998 !important;
        width: 360px !important;
        max-height: 500px !important;
        border-radius: 16px !important;
        background: #1a1b2e !important;
        box-shadow: 0 20px 60px rgba(0,0,0,.7) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        display: {win_display} !important;
        flex-direction: column !important;
        overflow: hidden !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}

    /* Header */
    #agri-header {{
        background: linear-gradient(135deg, #4e54c8, #8f94fb) !important;
        padding: 12px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        flex-shrink: 0 !important;
        color: white !important;
        min-height: 56px !important;
    }}
    #agri-header-left {{ 
        display: flex !important; 
        align-items: center !important; 
        gap: 10px !important; 
    }}
    .agri-avatar {{
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        background: rgba(255,255,255,.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 16px !important;
    }}
    .agri-title {{ 
        font-size: 14px !important; 
        font-weight: 600 !important; 
        margin: 0 !important; 
        line-height: 1.2 !important; 
    }}
    .agri-status {{ 
        font-size: 10px !important; 
        opacity: .8 !important; 
        margin: 0 !important; 
    }}
    .dot-green {{ color: #7bffb2 !important; }}
    
    #agri-close-btn {{
        background: rgba(255,255,255,.15) !important;
        border: none !important;
        color: white !important;
        font-size: 18px !important;
        width: 30px !important;
        height: 30px !important;
        border-radius: 50% !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background .2s !important;
        line-height: 1 !important;
        padding: 0 !important;
    }}
    #agri-close-btn:hover {{ background: rgba(255,255,255,.3) !important; }}

    /* Messages */
    #agri-messages {{
        flex: 1 !important;
        overflow-y: auto !important;
        padding: 12px 14px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
        scroll-behavior: smooth !important;
        scrollbar-width: thin !important;
        scrollbar-color: #3a3b55 transparent !important;
        max-height: 360px !important;
        min-height: 200px !important;
    }}
    #agri-messages::-webkit-scrollbar {{ width: 4px !important; }}
    #agri-messages::-webkit-scrollbar-thumb {{ 
        background: #3a3b55 !important; 
        border-radius: 4px !important; 
    }}

    /* Bubbles */
    .bubble {{
        max-width: 85% !important;
        padding: 8px 12px !important;
        border-radius: 12px !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
        word-wrap: break-word !important;
        margin-bottom: 2px !important;
    }}
    .bubble strong {{ font-weight: 600 !important; }}
    .bubble em {{ font-style: italic !important; }}
    .bubble code {{
        background: rgba(255,255,255,.1) !important;
        padding: 1px 4px !important;
        border-radius: 3px !important;
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

    /* Chat Input Area */
    #agri-input-area {{
        padding: 8px 12px !important;
        border-top: 1px solid rgba(255,255,255,.06) !important;
        background: #1a1b2e !important;
        flex-shrink: 0 !important;
        display: {input_display} !important;
    }}
    #agri-input-area input {{
        width: 100% !important;
        padding: 8px 12px !important;
        border-radius: 20px !important;
        border: 1.5px solid #4e54c8 !important;
        background: #12132a !important;
        color: #dde0ff !important;
        font-size: 13px !important;
        outline: none !important;
        box-sizing: border-box !important;
    }}
    #agri-input-area input::placeholder {{
        color: #6a6b8a !important;
    }}
    #agri-input-area input:focus {{
        border-color: #8f94fb !important;
    }}
    
    /* Hide default chat input when not needed */
    [data-testid="stChatInput"] {{
        display: none !important;
    }}
    </style>

    <!-- FAB Button -->
    <div id="agri-fab" onclick="toggleChat()">💬</div>

    <!-- Chat Window -->
    <div id="agri-chat-win">
        <div id="agri-header">
            <div id="agri-header-left">
                <div class="agri-avatar">🤖</div>
                <div>
                    <p class="agri-title">AgriTech Assistant</p>
                    <p class="agri-status"><span class="dot-green">●</span> Online</p>
                </div>
            </div>
            <button id="agri-close-btn" onclick="toggleChat()">✕</button>
        </div>
        <div id="agri-messages">
            {messages_html}
        </div>
        <div id="agri-input-area">
            <input type="text" id="agri-input" placeholder="Ask about inventory, orders, pricing…" />
        </div>
    </div>

    <script>
    function toggleChat() {{
        var url = new URL(window.location.href);
        if (url.searchParams.has('chat_toggle')) {{
            url.searchParams.delete('chat_toggle');
        }} else {{
            url.searchParams.set('chat_toggle', '1');
        }}
        window.location.href = url.toString();
    }}

    // Handle Enter key in chat input
    document.addEventListener('DOMContentLoaded', function() {{
        var input = document.getElementById('agri-input');
        if (input) {{
            input.addEventListener('keypress', function(e) {{
                if (e.key === 'Enter' && this.value.trim()) {{
                    // Create a hidden input to submit the message
                    var form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '';
                    
                    var msgInput = document.createElement('input');
                    msgInput.type = 'hidden';
                    msgInput.name = 'chat_message';
                    msgInput.value = this.value.trim();
                    form.appendChild(msgInput);
                    
                    document.body.appendChild(form);
                    form.submit();
                }}
            }});
        }}
        
        // Scroll to bottom of messages
        var messages = document.getElementById('agri-messages');
        if (messages) {{
            messages.scrollTop = messages.scrollHeight;
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)

    # ── Handle chat message submission ────────────────────────────
    # Check for form submission with chat message
    if st.session_state.get("chat_message"):
        prompt = st.session_state.chat_message
        st.session_state["chat_message"] = None  # Clear it
        
        if prompt and prompt.strip():
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})

            # Get AI response
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

            # Add assistant response
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()
