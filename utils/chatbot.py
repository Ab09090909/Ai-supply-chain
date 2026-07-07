"""Floating AI Support Chatbot — Top-Right Position, Polished UI."""
import os
import json
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# Initialize Groq client (Free)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# ─────────────────────────────────────────────
# DATABASE TOOLS
# ─────────────────────────────────────────────
def search_products(product_name=None, sector=None, region=None):
    try:
        from utils.db_helpers import supabase
        query = supabase.table("products").select("product_name, sector, region, price_birr, quantity, unit").limit(15)
        if product_name: query = query.ilike("product_name", f"%{product_name}%")
        if sector: query = query.eq("sector", sector)
        if region: query = query.eq("region", region)
        return json.dumps(query.execute().data or [])
    except Exception as e:
        return json.dumps({"error": str(e)})

def search_producers(region=None):
    try:
        from utils.db_helpers import supabase
        query = supabase.table("profiles").select("full_name, region, phone").eq("role", "producer").limit(15)
        if region: query = query.eq("region", region)
        return json.dumps(query.execute().data or [])
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_platform_stats():
    try:
        from utils.db_helpers import supabase
        from utils.constants import REGIONS
        p_count = supabase.table("products").select("id", count="exact").execute().count or 0
        u_count = supabase.table("profiles").select("id", count="exact").execute().count or 0
        return json.dumps({"total_products": p_count, "total_users": u_count, "supported_regions": REGIONS})
    except Exception as e:
        return json.dumps({"error": str(e)})

available_tools = {"search_products": search_products, "search_producers": search_producers, "get_platform_stats": get_platform_stats}

groq_tools = [
    {"type": "function", "function": {"name": "search_products", "description": "Search for products.", "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}, "sector": {"type": "string"}, "region": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "search_producers", "description": "Search for producers.", "parameters": {"type": "object", "properties": {"region": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "get_platform_stats", "description": "Get platform stats.", "parameters": {"type": "object", "properties": {}, "required": []}}}
]

# ─────────────────────────────────────────────
# JS INJECTOR
#
# Why JS instead of pure CSS: raw HTML written via st.markdown (e.g. a
# "<div>" opening tag) does NOT become a real parent of the Streamlit
# widgets that follow it in the code — each st.* call adds its own
# sibling node to the page. So a hand-written div can never wrap a
# button, a chat_input, etc. The only Streamlit call that creates a real
# parent for later widgets is st.container(). This script finds that
# real container (via an invisible marker placed inside it) and turns
# IT into the floating panel, and finds the FAB/clear/close buttons by
# their visible text (version-independent — no reliance on Streamlit's
# internal class names, which differ across releases).
# ─────────────────────────────────────────────
def inject_widget_js():
    components.html("""
    <script>
    function styleChatWidget() {
        try {
            const doc = window.parent.document;

            // ── FAB / clear / close buttons, matched by visible text ──
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(function(btn) {
                const txt = (btn.innerText || '').trim();

                if (txt === '\\ud83d\\udcac') { // 💬 FAB toggle
                    btn.style.setProperty('position', 'fixed', 'important');
                    btn.style.setProperty('top', '20px', 'important');
                    btn.style.setProperty('right', '24px', 'important');
                    btn.style.setProperty('left', 'auto', 'important');
                    btn.style.setProperty('z-index', '999999', 'important');
                    btn.style.setProperty('width', '56px', 'important');
                    btn.style.setProperty('height', '56px', 'important');
                    btn.style.setProperty('border-radius', '50%', 'important');
                    btn.style.setProperty('background', 'linear-gradient(135deg, #D4A017 0%, #F4C430 100%)', 'important');
                    btn.style.setProperty('color', '#1B4332', 'important');
                    btn.style.setProperty('font-size', '26px', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                    btn.style.setProperty('padding', '0', 'important');
                    btn.style.setProperty('box-shadow', '0 6px 20px rgba(0,0,0,0.4)', 'important');
                    btn.style.setProperty('cursor', 'pointer', 'important');
                    let p = btn.parentElement;
                    for (let i = 0; i < 5 && p; i++) {
                        p.style.setProperty('position', 'static', 'important');
                        p.style.setProperty('width', 'auto', 'important');
                        p.style.setProperty('min-width', '0px', 'important');
                        p = p.parentElement;
                    }
                } else if (txt === '\\ud83e\\uddf9') { // 🧹 clear
                    btn.style.setProperty('background', 'rgba(255,255,255,0.12)', 'important');
                    btn.style.setProperty('border', '1px solid rgba(255,255,255,0.22)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('width', '30px', 'important');
                    btn.style.setProperty('height', '30px', 'important');
                    btn.style.setProperty('min-width', '30px', 'important');
                    btn.style.setProperty('border-radius', '8px', 'important');
                    btn.style.setProperty('padding', '0', 'important');
                } else if (txt === '\\u2715') { // ✕ close
                    btn.style.setProperty('background', 'rgba(239,68,68,0.18)', 'important');
                    btn.style.setProperty('border', '1px solid rgba(239,68,68,0.35)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('width', '30px', 'important');
                    btn.style.setProperty('height', '30px', 'important');
                    btn.style.setProperty('min-width', '30px', 'important');
                    btn.style.setProperty('border-radius', '8px', 'important');
                    btn.style.setProperty('padding', '0', 'important');
                }
            });

            // ── The chat window itself: find the real st.container() via
            // the invisible marker, then style/position THAT node. ──
            const marker = doc.querySelector('#chat-window-marker');
            if (marker) {
                const panel = marker.closest('[data-testid="stVerticalBlock"]');
                if (panel && !panel.classList.contains('floating-chat-panel')) {
                    panel.classList.add('floating-chat-panel');
                }
            }

            // ── The header button row (clear/close columns): give it the
            // same header background so it reads as one continuous bar. ──
            const hMarker = doc.querySelector('#chat-header-btns-marker');
            if (hMarker) {
                const row = hMarker.closest('[data-testid="stHorizontalBlock"]');
                if (row && !row.classList.contains('chat-header-btns-row')) {
                    row.classList.add('chat-header-btns-row');
                }
            }
        } catch (e) {
            console.error('chat widget styling error', e);
        }
    }

    styleChatWidget();
    try {
        const observer = new MutationObserver(function() { styleChatWidget(); });
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
    } catch (e) {}
    setInterval(styleChatWidget, 400);
    </script>
    """, height=0, width=0)

# ─────────────────────────────────────────────
# RENDER THE FLOATING CHATBOT UI
# ─────────────────────────────────────────────
def render_floating_chatbot(user_profile):
    # 1. Inject CSS for elements we render directly, plus the classes that
    # inject_widget_js() attaches to the real Streamlit container/row.
    st.markdown("""
    <style>
    /* ── Label Under Icon ── */
    .chatbot-label {
        position: fixed !important;
        top: 80px !important;
        right: 24px !important;
        z-index: 999999 !important;
        background: #1B4332 !important;
        color: #F4C430 !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        text-align: center;
        pointer-events: none;
    }

    /* ── The chat window panel — this class is added by JS onto the real
       st.container() div, so everything rendered inside that container
       (header, buttons, messages, input) is an actual DOM child and
       therefore visually contained, scrollable, etc. Sized responsively
       so it never exceeds the viewport on small/mobile screens. ── */
    div.floating-chat-panel {
        position: fixed !important;
        top: min(112px, 10vh) !important;
        right: 16px !important;
        left: auto !important;
        width: min(380px, calc(100vw - 32px)) !important;
        height: min(520px, 72vh) !important;
        max-height: 72vh !important;
        z-index: 999998 !important;
        margin: 0 !important;
        background: #12161f !important;
        border: 1px solid #2a3344 !important;
        border-radius: 18px !important;
        box-shadow: 0 16px 48px rgba(0,0,0,0.55) !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        animation: chatFadeIn 0.18s ease-out;
    }
    @keyframes chatFadeIn {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Make sure padding/gap Streamlit normally adds inside a block doesn't
       leave odd gaps between our header/messages/input children. */
    div.floating-chat-panel > div { width: 100%; }

    /* Streamlit wraps every widget/markdown call in its own wrapper divs
       (element-container / stMarkdown / stMarkdownContainer). Those
       wrappers — not our custom <div>s — are the actual flex children of
       the panel, so flex:1 set on our own div was being ignored by the
       real layout. Collapsing the wrappers with display:contents makes
       our own divs (and Streamlit's real widgets) the direct flex
       children instead, so flex:1 / flex-shrink:0 behave correctly and
       the chat input never gets pushed out of view. */
    div.floating-chat-panel [data-testid="element-container"],
    div.floating-chat-panel [data-testid="stElementContainer"],
    div.floating-chat-panel [data-testid="stMarkdown"],
    div.floating-chat-panel [data-testid="stMarkdownContainer"] {
        display: contents !important;
    }
    /* Non-growing items keep their natural height so the messages area
       (flex:1 below) absorbs all remaining space and scrolls. */
    div.floating-chat-panel .chat-header-bar,
    div.floating-chat-panel .chat-header-btns-row,
    div.floating-chat-panel .stChatInput {
        flex-shrink: 0 !important;
    }

    /* ── Header ── */
    .chat-header-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 12px 12px 16px;
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
    }
    .chat-avatar {
        width: 34px; height: 34px; border-radius: 50%;
        background: linear-gradient(135deg, #F4C430, #D4A017);
        display: flex; align-items: center; justify-content: center;
        font-size: 17px; flex-shrink: 0;
    }
    .chat-header-text { flex: 1; min-width: 0; }
    .chat-header-title { font-weight: 700; font-size: 14.5px; color: #ffffff; line-height: 1.2; }
    .chat-header-status { font-size: 11px; color: #B7E4C7; display: flex; align-items: center; gap: 5px; margin-top: 2px; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ADE80; display: inline-block; box-shadow: 0 0 6px #4ADE80; }

    /* Row holding the Clear / Close buttons — JS tags the real Streamlit
       horizontal-block with this class so it matches the header's bg.
       Streamlit auto-stacks st.columns() vertically on narrow/mobile
       viewports; force it back to a horizontal row here. */
    div.chat-header-btns-row {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important;
        padding: 2px 10px 8px 10px !important;
        margin-top: -6px !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: flex-end !important;
        align-items: center !important;
        gap: 8px !important;
    }
    div.chat-header-btns-row > [data-testid="stColumn"] {
        width: auto !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
        max-width: none !important;
    }

    /* ── Message Area ── */
    div.floating-chat-panel .chat-messages-area {
        flex: 1 1 auto !important;
        min-height: 0 !important;
        overflow-y: auto !important;
        padding: 14px 12px;
        background: #0d1017;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .chat-messages-area::-webkit-scrollbar { width: 5px; }
    .chat-messages-area::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

    .msg-row { display: flex; width: 100%; }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.assistant { justify-content: flex-start; }

    .msg-bubble {
        max-width: 80%;
        padding: 9px 13px;
        font-size: 13.5px;
        line-height: 1.45;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .msg-bubble.user {
        background: linear-gradient(135deg, #2D6A4F, #1B4332);
        color: #ffffff;
        border-radius: 14px 14px 3px 14px;
    }
    .msg-bubble.assistant {
        background: #1e2532;
        color: #e5e7eb;
        border: 1px solid #2a3344;
        border-radius: 14px 14px 14px 3px;
    }

    /* ── Input Area ── */
    div.floating-chat-panel .stChatInput {
        padding: 10px 12px !important;
        background: #12161f !important;
        border-top: 1px solid #2a3344 !important;
        flex-shrink: 0 !important;
    }
    div.floating-chat-panel .stChatInput textarea {
        background: #1e2532 !important;
        color: #e5e7eb !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Initialize Session State
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "chat_messages" not in st.session_state:
        role = user_profile.get("role", "user") if user_profile else "guest"
        name = user_profile.get("full_name", "User") if user_profile else "Guest"
        st.session_state.chat_messages = [
            {"role": "system", "content": f"You are the Assistant AI for the Ethiopian AI Supply Chain Platform. The current user is a {role} named {name}. You have access to live database tools. Be helpful, concise, and professional."}
        ]

    # 3. Render the Floating Action Button (FAB) - Top Right
    if st.button("💬", key="fab_chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # 4. Render the Label Under the Icon
    st.markdown('<div class="chatbot-label">Assistant AI</div>', unsafe_allow_html=True)

    # 5. Render the Chat Window (if open) — everything below lives inside
    # ONE real st.container(), which is what inject_widget_js() finds and
    # turns into the floating panel.
    if st.session_state.chat_open:
        with st.container():
            # Invisible marker so JS can locate this exact container.
            st.markdown('<span id="chat-window-marker" style="display:none"></span>', unsafe_allow_html=True)

            # ── Header: avatar + title/status ──
            st.markdown("""
            <div class="chat-header-bar">
                <div class="chat-avatar">💬</div>
                <div class="chat-header-text">
                    <div class="chat-header-title">Assistant AI</div>
                    <div class="chat-header-status"><span class="status-dot"></span>Online now</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Clear / Close buttons ──
            st.markdown('<span id="chat-header-btns-marker" style="display:none"></span>', unsafe_allow_html=True)
            col_clear, col_close = st.columns(2)
            with col_clear:
                if st.button("🧹", key="clear_chat_icon", help="Clear chat history"):
                    st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                    st.rerun()
            with col_close:
                if st.button("✕", key="close_chat_icon", help="Close chat"):
                    st.session_state.chat_open = False
                    st.rerun()

            # ── Messages Area ──
            messages_html = '<div class="chat-messages-area">'
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    text = (msg.get("content") or "").replace("<", "&lt;").replace(">", "&gt;")
                    messages_html += f'<div class="msg-row user"><div class="msg-bubble user">{text}</div></div>'
                elif msg["role"] == "assistant" and msg.get("content"):
                    text = (msg.get("content") or "").replace("<", "&lt;").replace(">", "&gt;")
                    messages_html += f'<div class="msg-row assistant"><div class="msg-bubble assistant">{text}</div></div>'
            messages_html += '</div>'
            st.markdown(messages_html, unsafe_allow_html=True)

            # ── Input Area ──
            prompt = st.chat_input("Ask about products, producers...", key="floating_chat_input")

            if prompt:
                if not client:
                    st.error("⚠️ GROQ_API_KEY missing.")
                else:
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})

                    with st.spinner("Assistant is typing..."):
                        try:
                            response = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=st.session_state.chat_messages,
                                tools=groq_tools,
                                tool_choice="auto",
                                temperature=0.6,
                                max_tokens=800
                            )
                            response_message = response.choices[0].message
                            tool_calls = response_message.tool_calls

                            if tool_calls:
                                st.session_state.chat_messages.append({
                                    "role": response_message.role,
                                    "content": response_message.content or "",
                                    "tool_calls": response_message.tool_calls
                                })
                                for tool_call in tool_calls:
                                    function_name = tool_call.function.name
                                    function_to_call = available_tools[function_name]
                                    function_args = json.loads(tool_call.function.arguments)
                                    function_response = function_to_call(**function_args)
                                    st.session_state.chat_messages.append({
                                        "tool_call_id": tool_call.id,
                                        "role": "tool",
                                        "name": function_name,
                                        "content": function_response,
                                    })
                                second_response = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=st.session_state.chat_messages,
                                )
                                ai_reply = second_response.choices[0].message.content
                            else:
                                ai_reply = response_message.content

                            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.rerun()

    # 6. Apply JS-based styling/positioning last, so the marker(s) above
    # already exist in the DOM by the time this runs.
    inject_widget_js()
