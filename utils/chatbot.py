"""Floating AI Support Chatbot — Top-Right Position, Polished UI."""
import os
import json
import streamlit as st
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
# RENDER THE FLOATING CHATBOT UI
# ─────────────────────────────────────────────
def render_floating_chatbot(user_profile):
    # 1. Inject CSS — fixed TOP-RIGHT positioning + polished visual design
    st.markdown("""
    <style>
    /* ── Floating Action Button (FAB) - Fixed Top Right ──
       Streamlit does not expose key="..." as a real HTML attribute on the
       button element, so it must be targeted via the auto-generated
       st-key-<key> class on the widget's wrapper div instead. */
    div[class*="st-key-fab_chat_toggle"] {
        position: fixed !important;
        top: 20px !important;
        right: 24px !important;
        left: auto !important;
        z-index: 999999 !important;
        width: 56px !important;
        height: 56px !important;
    }
    div[class*="st-key-fab_chat_toggle"] > div,
    div[class*="st-key-fab_chat_toggle"] .stButton {
        width: 56px !important;
        height: 56px !important;
    }
    div[class*="st-key-fab_chat_toggle"] button {
        width: 56px !important;
        height: 56px !important;
        background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
        color: #1B4332 !important;
        border-radius: 50% !important;
        font-size: 26px !important;
        padding: 0 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
        border: none !important;
        transition: transform 0.2s ease !important;
    }
    div[class*="st-key-fab_chat_toggle"] button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
    }

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

    /* ── Chat Window - Fixed Below Button (Top Right) ──
       :has() targets the nearest real ancestor block that contains the
       .floating-chat-box marker div, which is what actually needs to be
       pinned to the viewport (the marker div itself has no box). */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.floating-chat-box),
    div[data-testid="stVerticalBlock"]:has(> div.floating-chat-box) {
        position: fixed !important;
        top: 112px !important;
        right: 24px !important;
        left: auto !important;
        width: 380px !important;
        height: 560px !important;
        z-index: 999998 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .floating-chat-box {
        background: #12161f;
        border: 1px solid #2a3344;
        border-radius: 18px;
        box-shadow: 0 16px 48px rgba(0,0,0,0.55);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        height: 100%;
        animation: chatFadeIn 0.2s ease-out;
    }
    @keyframes chatFadeIn {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Header ── */
    .chat-header-wrap { background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%); }
    .chat-header-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 12px 14px 16px;
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

    /* Header icon buttons (Clear / Close) rendered via st.button inside header row.
       Same fix as the FAB: target the real st-key-<key> wrapper class. */
    div[data-testid="stHorizontalBlock"]:has(.header-anchor) { align-items: center !important; }

    div[class*="st-key-clear_chat_icon"] button,
    div[class*="st-key-close_chat_icon"] button {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        color: #ffffff !important;
        font-size: 14px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        min-height: 30px !important;
        max-height: 30px !important;
        width: 30px !important;
        min-width: 30px !important;
        max-width: 30px !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s !important;
    }
    div[class*="st-key-clear_chat_icon"] button:hover,
    div[class*="st-key-close_chat_icon"] button:hover {
        background: rgba(255,255,255,0.25) !important;
        border-color: rgba(255,255,255,0.45) !important;
    }
    div[class*="st-key-close_chat_icon"] button {
        background: rgba(239,68,68,0.18) !important;
        border-color: rgba(239,68,68,0.35) !important;
    }
    div[class*="st-key-close_chat_icon"] button:hover {
        background: rgba(239,68,68,0.35) !important;
        border-color: rgba(239,68,68,0.55) !important;
    }

    /* ── Message Area ── */
    .chat-messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 16px 14px;
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
    .msg-typing { display: flex; gap: 4px; padding: 4px 2px; }
    .msg-typing span {
        width: 6px; height: 6px; border-radius: 50%;
        background: #94a3b8; opacity: 0.6;
        animation: typingBounce 1s infinite ease-in-out;
    }
    .msg-typing span:nth-child(2) { animation-delay: 0.15s; }
    .msg-typing span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-4px); } }

    /* ── Input Area ── */
    .floating-chat-box .stChatInput {
        padding: 10px 12px !important;
        background: #12161f !important;
        border-top: 1px solid #2a3344 !important;
    }
    .floating-chat-box .stChatInput textarea {
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

    # 5. Render the Chat Window (if open)
    if st.session_state.chat_open:
        with st.container():
            st.markdown('<div class="floating-chat-box">', unsafe_allow_html=True)

            # ── Header: avatar + title/status + clear/close buttons ──
            st.markdown('<div class="chat-header-wrap"><span class="header-anchor"></span>', unsafe_allow_html=True)
            col_title, col_clear, col_close = st.columns([5, 1, 1])
            with col_title:
                st.markdown("""
                <div class="chat-header-bar">
                    <div class="chat-avatar">💬</div>
                    <div class="chat-header-text">
                        <div class="chat-header-title">Assistant AI</div>
                        <div class="chat-header-status"><span class="status-dot"></span>Online now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_clear:
                if st.button("🧹", key="clear_chat_icon", help="Clear chat history"):
                    st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                    st.rerun()
            with col_close:
                if st.button("✕", key="close_chat_icon", help="Close chat"):
                    st.session_state.chat_open = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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

            st.markdown('</div>', unsafe_allow_html=True)
