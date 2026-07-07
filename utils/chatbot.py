"""Floating AI Support Chatbot — Fixed Position & Updated UI."""
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
    # 1. Inject Robust CSS for Fixed Positioning
    st.markdown("""
    <style>
    /* ── Floating Action Button (FAB) - Fixed Bottom Right ─ */
    .stButton > button[key="fab_chat_toggle"] {
        position: fixed !important;
        bottom: 25px !important;
        right: 25px !important;
        z-index: 999999 !important;
        background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
        color: #1B4332 !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        font-size: 28px !important;
        padding: 0 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
        border: none !important;
        transition: transform 0.2s !important;
    }
    .stButton > button[key="fab_chat_toggle"]:hover {
        transform: scale(1.1) !important;
    }

    /* ─ Chat Window - Fixed Above Button ── */
    div[data-testid="stVerticalBlock"] > div:has(> div.floating-chat-box) {
        position: fixed !important;
        bottom: 100px !important;
        right: 25px !important;
        width: 380px !important;
        height: 550px !important;
        z-index: 999998 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .floating-chat-box {
        background: #161b27;
        border: 1px solid #334155;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        height: 100%;
    }
    
    /* ── Header Styling ── */
    .chat-header-bar {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #334155;
    }
    
    /* ── Icon Buttons in Header ── */
    .header-icon-btn > button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-size: 18px !important;
        padding: 4px 8px !important;
        margin: 0 !important;
        min-height: auto !important;
        width: auto !important;
    }
    .header-icon-btn > button:hover {
        color: #F4C430 !important;
        background: rgba(255,255,255,0.1) !important;
        border-radius: 6px !important;
    }

    /* ─ Chat Area ── */
    .chat-messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background: #0f1117;
    }
    .floating-chat-box [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
    }
    .floating-chat-box .stChatInput {
        padding: 12px !important;
        background: #161b27 !important;
        border-top: 1px solid #334155 !important;
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

    # 3. Render the Floating Action Button (FAB)
    # This button stays fixed at the bottom right
    if st.button("💬", key="fab_chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # 4. Render the Chat Window (if open)
    if st.session_state.chat_open:
        with st.container():
            st.markdown('<div class="floating-chat-box">', unsafe_allow_html=True)
            
            # ── Header with Title and Icon Buttons ──
            st.markdown("""
            <div class="chat-header-bar">
                <div>
                    <div style="font-weight: 700; font-size: 16px; color: white;">💬 Assistant AI</div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.7);">Support Chatbot</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Icon Buttons Row (Clear and Close)
            col_clear, col_close = st.columns([1, 1])
            with col_clear:
                st.markdown('<div class="header-icon-btn">', unsafe_allow_html=True)
                if st.button("️", key="clear_chat_icon", help="Clear Chat History"):
                    # Keep the system prompt, clear the rest
                    st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_close:
                st.markdown('<div class="header-icon-btn">', unsafe_allow_html=True)
                if st.button("❌", key="close_chat_icon", help="Close Chat"):
                    st.session_state.chat_open = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Messages Area ──
            with st.container():
                st.markdown('<div class="chat-messages-area">', unsafe_allow_html=True)
                for msg in st.session_state.chat_messages:
                    if msg["role"] not in ("system", "tool"):
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Input Area ──
            prompt = st.chat_input("Ask about products, producers...", key="floating_chat_input")
            
            if prompt:
                if not client:
                    st.error("️ GROQ_API_KEY missing.")
                else:
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    
                    with st.chat_message("assistant"):
                        with st.spinner("🧠 Thinking..."):
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

                                st.write(ai_reply)
                                st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
                            except Exception as e:
                                st.error(f"Error: {e}")
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
