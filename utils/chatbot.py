"""Floating AI Support Chatbot — Top-Right Position, Polished UI."""
import os
import json
import logging
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, List
from groq import Groq

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# GROQ CLIENT INITIALIZATION
# ─────────────────────────────────────────────
def get_groq_client():
    """Lazy initialize Groq client with better error handling."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Check if it's in st.secrets (Streamlit Cloud)
        try:
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                api_key = st.secrets['GROQ_API_KEY']
                os.environ['GROQ_API_KEY'] = api_key
            else:
                logger.warning("GROQ_API_KEY not found in environment or secrets")
                return None
        except Exception as e:
            logger.error(f"Error accessing secrets: {e}")
            return None
    
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Groq client initialization error: {e}")
        return None

# ─────────────────────────────────────────────
# DATABASE TOOLS WITH BETTER ERROR HANDLING
# ─────────────────────────────────────────────
def get_db():
    """Lazy import db_helpers to avoid circular imports."""
    try:
        from utils.db_helpers import supabase
        return supabase
    except ImportError as e:
        logger.error(f"Failed to import db_helpers: {e}")
        return None

def search_products(product_name: Optional[str] = None, sector: Optional[str] = None, region: Optional[str] = None) -> str:
    """
    Search for products in the database.
    
    Args:
        product_name: Optional product name to search for
        sector: Optional sector filter
        region: Optional region filter
    
    Returns:
        JSON string with search results or error
    """
    try:
        supabase = get_db()
        if not supabase:
            return json.dumps({"error": "Database connection unavailable"})
        
        # Build query
        query = supabase.table("products").select("product_name, sector, region, price_birr, quantity, unit, created_at").limit(15)
        
        if product_name and product_name.strip():
            query = query.ilike("product_name", f"%{product_name.strip()}%")
        if sector and sector.strip():
            query = query.eq("sector", sector.strip())
        if region and region.strip():
            query = query.eq("region", region.strip())
        
        # Execute query
        response = query.execute()
        
        if response and response.data:
            return json.dumps(response.data)
        else:
            return json.dumps({"message": "No products found matching your criteria."})
            
    except Exception as e:
        logger.error(f"Product search error: {e}")
        return json.dumps({"error": f"Search failed: {str(e)}"})

def search_producers(region: Optional[str] = None) -> str:
    """
    Search for producers in the database.
    
    Args:
        region: Optional region filter
    
    Returns:
        JSON string with search results or error
    """
    try:
        supabase = get_db()
        if not supabase:
            return json.dumps({"error": "Database connection unavailable"})
        
        query = supabase.table("profiles").select("full_name, region, phone, is_verified").eq("role", "producer").limit(15)
        
        if region and region.strip():
            query = query.eq("region", region.strip())
        
        response = query.execute()
        
        if response and response.data:
            return json.dumps(response.data)
        else:
            return json.dumps({"message": "No producers found matching your criteria."})
            
    except Exception as e:
        logger.error(f"Producer search error: {e}")
        return json.dumps({"error": f"Search failed: {str(e)}"})

def get_platform_stats() -> str:
    """
    Get platform statistics.
    
    Returns:
        JSON string with platform statistics or error
    """
    try:
        supabase = get_db()
        if not supabase:
            return json.dumps({"error": "Database connection unavailable"})
        
        # Get product count
        try:
            p_response = supabase.table("products").select("id", count="exact").execute()
            p_count = p_response.count if p_response else 0
        except Exception:
            p_count = 0
        
        # Get user count
        try:
            u_response = supabase.table("profiles").select("id", count="exact").execute()
            u_count = u_response.count if u_response else 0
        except Exception:
            u_count = 0
        
        # Get regions from constants
        try:
            from utils.constants import REGIONS
            regions = REGIONS
        except ImportError:
            regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "Sidama", "SNNPR"]
        
        return json.dumps({
            "total_products": p_count,
            "total_users": u_count,
            "supported_regions": regions,
            "active_sectors": ["Agriculture", "Manufacturing", "Trade", "Technology", "Services"]
        })
        
    except Exception as e:
        logger.error(f"Platform stats error: {e}")
        return json.dumps({"error": f"Failed to get stats: {str(e)}"})

# Tool definitions for Groq
available_tools = {
    "search_products": search_products,
    "search_producers": search_producers,
    "get_platform_stats": get_platform_stats
}

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in the supply chain platform by name, sector, or region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to search for (e.g., 'coffee', 'teff')"
                    },
                    "sector": {
                        "type": "string",
                        "description": "The sector/category of the product (e.g., 'Agriculture', 'Manufacturing')"
                    },
                    "region": {
                        "type": "string",
                        "description": "The region where the product is available (e.g., 'Oromia', 'Amhara')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_producers",
            "description": "Search for producers/suppliers in the platform by region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "The region to search for producers (e.g., 'Oromia', 'Addis Ababa')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_platform_stats",
            "description": "Get overall platform statistics including total products, users, and supported regions.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# ─────────────────────────────────────────────
# JS INJECTOR FOR FLOATING WIDGET
# ─────────────────────────────────────────────
def inject_widget_js():
    """Inject JavaScript to style and position the chat widget."""
    components.html("""
    <script>
    function styleChatWidget() {
        try {
            const doc = window.parent.document;

            // ── FAB / clear / close buttons ──
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(function(btn) {
                const txt = (btn.innerText || '').trim();

                if (txt === '💬') {
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
                    btn.style.setProperty('transition', 'transform 0.2s', 'important');
                    
                    // Hover effect
                    btn.addEventListener('mouseenter', function() {
                        this.style.transform = 'scale(1.1)';
                    });
                    btn.addEventListener('mouseleave', function() {
                        this.style.transform = 'scale(1)';
                    });
                    
                    let p = btn.parentElement;
                    for (let i = 0; i < 5 && p; i++) {
                        p.style.setProperty('position', 'static', 'important');
                        p.style.setProperty('width', 'auto', 'important');
                        p.style.setProperty('min-width', '0px', 'important');
                        p = p.parentElement;
                    }
                } else if (txt === '🧹') {
                    btn.style.setProperty('background', 'rgba(255,255,255,0.12)', 'important');
                    btn.style.setProperty('border', '1px solid rgba(255,255,255,0.22)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('width', '30px', 'important');
                    btn.style.setProperty('height', '30px', 'important');
                    btn.style.setProperty('min-width', '30px', 'important');
                    btn.style.setProperty('border-radius', '8px', 'important');
                    btn.style.setProperty('padding', '0', 'important');
                    btn.style.setProperty('transition', 'all 0.2s', 'important');
                    
                    btn.addEventListener('mouseenter', function() {
                        this.style.background = 'rgba(255,255,255,0.2)';
                    });
                    btn.addEventListener('mouseleave', function() {
                        this.style.background = 'rgba(255,255,255,0.12)';
                    });
                } else if (txt === '✕') {
                    btn.style.setProperty('background', 'rgba(239,68,68,0.18)', 'important');
                    btn.style.setProperty('border', '1px solid rgba(239,68,68,0.35)', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('width', '30px', 'important');
                    btn.style.setProperty('height', '30px', 'important');
                    btn.style.setProperty('min-width', '30px', 'important');
                    btn.style.setProperty('border-radius', '8px', 'important');
                    btn.style.setProperty('padding', '0', 'important');
                    btn.style.setProperty('transition', 'all 0.2s', 'important');
                    
                    btn.addEventListener('mouseenter', function() {
                        this.style.background = 'rgba(239,68,68,0.3)';
                    });
                    btn.addEventListener('mouseleave', function() {
                        this.style.background = 'rgba(239,68,68,0.18)';
                    });
                }
            });

            // ── Chat window panel ──
            const marker = doc.querySelector('#chat-window-marker');
            if (marker) {
                const panel = marker.closest('[data-testid="stVerticalBlock"]');
                if (panel && !panel.classList.contains('floating-chat-panel')) {
                    panel.classList.add('floating-chat-panel');
                }
            }

            // ── Header buttons row ──
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
# CHATBOT UI RENDERER
# ─────────────────────────────────────────────
def render_floating_chatbot(user_profile: Optional[Dict[str, Any]] = None):
    """
    Render the floating chatbot UI.
    
    Args:
        user_profile: Optional user profile dictionary
    """
    # Check if Groq is available
    client = get_groq_client()
    
    # Initialize session state
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "chat_messages" not in st.session_state:
        role = user_profile.get("role", "guest") if user_profile else "guest"
        name = user_profile.get("full_name", "Guest") if user_profile else "Guest"
        
        system_prompt = f"""You are the Assistant AI for the Ethiopian AI Supply Chain Platform.
Current user: {name} (Role: {role})
Available Tools: search_products, search_producers, get_platform_stats

Guidelines:
1. Be helpful, concise, and professional
2. Use available tools to answer user questions about products, producers, and platform stats
3. If you don't know something, say so honestly
4. Keep responses under 500 words
5. For product searches, always include price and region if available
6. When listing products, format them clearly with bullet points
"""
        st.session_state.chat_messages = [
            {"role": "system", "content": system_prompt}
        ]

    # ── CSS for floating widget ──
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

    /* ── Chat window panel ── */
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
    
    div.floating-chat-panel > div { width: 100%; }

    div.floating-chat-panel [data-testid="element-container"],
    div.floating-chat-panel [data-testid="stElementContainer"],
    div.floating-chat-panel [data-testid="stMarkdown"],
    div.floating-chat-panel [data-testid="stMarkdownContainer"] {
        display: contents !important;
    }
    
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

    /* ── Header buttons row ── */
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
    
    /* ── Error message styling ── */
    .chat-error {
        color: #ef4444;
        font-size: 13px;
        padding: 8px 12px;
        background: rgba(239, 68, 68, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── FAB Button ──
    if st.button("💬", key="fab_chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # ── Label ──
    st.markdown('<div class="chatbot-label">Assistant AI</div>', unsafe_allow_html=True)

    # ── Chat Window ──
    if st.session_state.chat_open:
        with st.container():
            st.markdown('<span id="chat-window-marker" style="display:none"></span>', unsafe_allow_html=True)

            # Header
            st.markdown("""
            <div class="chat-header-bar">
                <div class="chat-avatar">💬</div>
                <div class="chat-header-text">
                    <div class="chat-header-title">Assistant AI</div>
                    <div class="chat-header-status"><span class="status-dot"></span>Online now</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Clear/Close buttons
            st.markdown('<span id="chat-header-btns-marker" style="display:none"></span>', unsafe_allow_html=True)
            col_clear, col_close = st.columns(2)
            with col_clear:
                if st.button("🧹", key="clear_chat_icon", help="Clear chat history"):
                    # Keep only system prompt
                    system_msg = st.session_state.chat_messages[0] if st.session_state.chat_messages else None
                    if system_msg and system_msg.get("role") == "system":
                        st.session_state.chat_messages = [system_msg]
                    else:
                        st.session_state.chat_messages = []
                    st.rerun()
            with col_close:
                if st.button("✕", key="close_chat_icon", help="Close chat"):
                    st.session_state.chat_open = False
                    st.rerun()

            # Messages
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

            # Input
            prompt = st.chat_input("Ask about products, producers...", key="floating_chat_input")

            if prompt:
                if not client:
                    st.error("⚠️ AI service unavailable. Please contact support.")
                else:
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})

                    with st.spinner("Assistant is thinking..."):
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
                                # Add assistant message with tool calls
                                st.session_state.chat_messages.append({
                                    "role": response_message.role,
                                    "content": response_message.content or "",
                                    "tool_calls": response_message.tool_calls
                                })
                                
                                # Execute tool calls
                                for tool_call in tool_calls:
                                    function_name = tool_call.function.name
                                    if function_name in available_tools:
                                        try:
                                            function_to_call = available_tools[function_name]
                                            function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                                            function_response = function_to_call(**function_args)
                                        except Exception as e:
                                            logger.error(f"Tool execution error: {e}")
                                            function_response = json.dumps({"error": f"Tool execution failed: {str(e)}"})
                                        
                                        st.session_state.chat_messages.append({
                                            "tool_call_id": tool_call.id,
                                            "role": "tool",
                                            "name": function_name,
                                            "content": function_response,
                                        })
                                    else:
                                        st.session_state.chat_messages.append({
                                            "tool_call_id": tool_call.id,
                                            "role": "tool",
                                            "name": function_name,
                                            "content": json.dumps({"error": f"Tool {function_name} not found"}),
                                        })
                                
                                # Get final response
                                second_response = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=st.session_state.chat_messages,
                                    max_tokens=800
                                )
                                ai_reply = second_response.choices[0].message.content or "I processed your request. Let me know if you need more information!"
                            else:
                                ai_reply = response_message.content or "I'm not sure how to respond. Could you rephrase your question?"

                            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
                            
                        except Exception as e:
                            logger.error(f"Chat error: {e}")
                            error_msg = "Sorry, I encountered an error. Please try again later."
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                            st.error(f"Chat error: {str(e)}")
                    
                    st.rerun()

    # ── Apply JS styling ──
    inject_widget_js()

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def is_chat_available() -> bool:
    """Check if the chat feature is available."""
    return get_groq_client() is not None

def get_chat_status() -> Dict[str, Any]:
    """Get the current chat status."""
    return {
        "available": is_chat_available(),
        "open": st.session_state.get("chat_open", False),
        "message_count": len(st.session_state.get("chat_messages", []))
    }
