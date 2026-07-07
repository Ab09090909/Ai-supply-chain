"""Floating AI Support Chatbot — Free Groq Llama 3 with Database Tools."""
import os
import json
import streamlit as st
from groq import Groq

# Initialize Groq client (Free)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# ─────────────────────────────────────────────
# DATABASE TOOLS
# ────────────────────────────────────────────
def search_products(product_name=None, sector=None, region=None):
    try:
        from utils.db_helpers import supabase
        query = supabase.table("products").select(
            "product_name, sector, region, price_birr, quantity, unit"
        ).limit(15)
        if product_name:
            query = query.ilike("product_name", f"%{product_name}%")
        if sector:
            query = query.eq("sector", sector)
        if region:
            query = query.eq("region", region)
        res = query.execute().data
        return json.dumps(res if res else [])
    except Exception as e:
        return json.dumps({"error": str(e)})

def search_producers(region=None):
    try:
        from utils.db_helpers import supabase
        query = supabase.table("profiles").select(
            "full_name, region, phone"
        ).eq("role", "producer").limit(15)
        if region:
            query = query.eq("region", region)
        res = query.execute().data
        return json.dumps(res if res else [])
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_platform_stats():
    try:
        from utils.db_helpers import supabase
        from utils.constants import REGIONS
        p_count = supabase.table("products").select("id", count="exact").execute().count or 0
        u_count = supabase.table("profiles").select("id", count="exact").execute().count or 0
        return json.dumps({
            "total_products": p_count,
            "total_users": u_count,
            "supported_regions": REGIONS
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

available_tools = {
    "search_products": search_products,
    "search_producers": search_producers,
    "get_platform_stats": get_platform_stats,
}

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Name of the product (e.g., 'Teff', 'Coffee')"},
                    "sector": {"type": "string", "description": "Sector to filter by"},
                    "region": {"type": "string", "description": "Region to filter by"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_producers",
            "description": "Search for producers in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Region to filter by"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_platform_stats",
            "description": "Get general statistics about the platform.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# ─────────────────────────────────────────────
# RENDER THE FLOATING CHATBOT UI
# ─────────────────────────────────────────────
def render_floating_chatbot(user_profile):
    """Render the floating chatbot button and window on any page."""

    # 1. Inject CSS for Floating Button + Chat Window
    st.markdown("""
    <style>
    /* Floating Action Button (FAB) */
    .stButton > button[key="fab_chat_toggle"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
        background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
        color: #1B4332 !important;
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        font-size: 32px !important;
        padding: 0 !important;
        box-shadow: 0 8px 25px rgba(212, 160, 23, 0.5) !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.2s !important;
    }
    .stButton > button[key="fab_chat_toggle"]:hover {
        transform: scale(1.1) !important;
    }

    /* Floating Chat Window */
    div[data-testid="stVerticalBlock"] > div:has(> div.floating-chat-box) {
        position: fixed !important;
        bottom: 110px !important;
        right: 30px !important;
        width: 400px !important;
        height: 600px !important;
        z-index: 9998 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .floating-chat-box {
        background: #161b27;
        border: 1px solid #334155;
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        height: 100%;
    }
    .chat-header-bar {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: white;
        padding: 18px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        font-size: 16px;
    }
    .chat-exit-btn {
        background: #ef4444 !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        font-size: 18px !important;
        padding: 0 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background 0.2s !important;
    }
    .chat-exit-btn:hover {
        background: #dc2626 !important;
    }
    .chat-messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #0f1117;
    }
    .floating-chat-box [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
    }
    .floating-chat-box .stChatInput {
        padding: 15px !important;
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
            {"role": "system", "content": f"You are the AI Support Assistant for the Ethiopian AI Supply Chain Platform. The current user is a {role} named {name}. You have access to live database tools. If the user asks about specific products, producers, prices, or regions, YOU MUST use the provided tools to fetch the data before answering. Be helpful, concise, and professional. Format lists using bullet points."}
        ]

    # 3. Render the Floating Action Button (FAB)
    if st.button("", key="fab_chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # 4. Render the Chat Window (if open)
    if st.session_state.chat_open:
        with st.container():
            st.markdown('<div class="floating-chat-box">', unsafe_allow_html=True)

            # Header with Exit Button
            st.markdown("""
            <div class="chat-header-bar">
                <span>💬 AI Support</span>
                <span style="font-size: 12px; opacity: 0.8; font-weight: 400;">🧠 Database Connected</span>
            </div>
            """, unsafe_allow_html=True)

            # Exit Button (placed right below header)
            with st.container():
                st.markdown('<div style="padding: 10px 20px; background: #161b27; border-bottom: 1px solid #334155; text-align: right;">', unsafe_allow_html=True)
                if st.button(" Exit Chat", key="exit_chat_btn", use_container_width=False):
                    st.session_state.chat_open = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Messages Area
            with st.container():
                st.markdown('<div class="chat-messages-area">', unsafe_allow_html=True)
                for msg in st.session_state.chat_messages:
                    if msg["role"] not in ("system", "tool"):
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])
                st.markdown('</div>', unsafe_allow_html=True)

            # Input Area
            prompt = st.chat_input(
                "Ask about products, producers, or regions...",
                key="floating_chat_input"
            )

            if prompt:
                if not client:
                    st.error("⚠️ GROQ_API_KEY missing in environment variables.")
                else:
                    st.session_state.chat_messages.append(
                        {"role": "user", "content": prompt}
                    )

                    with st.chat_message("assistant"):
                        with st.spinner("🔍 Searching database..."):
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
                                st.session_state.chat_messages.append({
                                    "role": "assistant",
                                    "content": ai_reply
                                })

                            except Exception as e:
                                st.error(f"Error: {e}")

                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
