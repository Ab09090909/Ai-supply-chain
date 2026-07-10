import os
import streamlit as st
from groq import Groq
from streamlit_float import *

# Initialize the float feature globally
float_init()

def get_groq_client():
    """Initialize Groq client using Streamlit secrets or environment variables."""
    # Try to get key from Streamlit secrets (for Streamlit Cloud) or .env (for local)
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        st.error("Groq API Key not found. Please add it to .streamlit/secrets.toml or .env file.")
        return None
    return Groq(api_key=api_key)

@st.cache_resource
def init_groq_client():
    return get_groq_client()

def inject_chatbot_styles():
    """Inject professional CSS to make the Streamlit chat look like a modern SaaS widget."""
    st.markdown("""
    <style>
    /* --- Floating Container Styling --- */
    .chat-widget-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 550px;
        width: 380px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .chat-widget-container {
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    }

    /* --- Chat Header --- */
    .chat-header {
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        padding: 16px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
    }
    .chat-header-info { display: flex; align-items: center; gap: 12px; }
    .chat-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: rgba(255,255,255,0.2); display: flex; 
        align-items: center; justify-content: center; font-size: 20px;
    }
    .chat-title { font-size: 16px; font-weight: 600; margin: 0; }
    .chat-subtitle { font-size: 12px; opacity: 0.8; margin: 0; }
    
    /* --- Chat Messages Area --- */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        scrollbar-width: thin;
    }
    .chat-messages::-webkit-scrollbar { width: 6px; }
    .chat-messages::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }

    /* Override Streamlit default chat styles to look like modern bubbles */
    div[data-testid="stChatMessage"] {
        background: transparent;
        padding: 4px 0;
        border: none;
    }
    div[data-testid="stChatMessageContent"] {
        background: #f1f3f5;
        padding: 10px 14px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* User messages on the right */
    div[data-testid="stChatMessage"]:has(div[data-testid="chat-avatar-user"]) {
        flex-direction: row-reverse;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chat-avatar-user"]) div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        color: white;
    }

    /* --- Chat Input Area --- */
    .chat-input-area {
        padding: 12px 16px;
        border-top: 1px solid rgba(0,0,0,0.05);
        background: rgba(255,255,255,0.8);
    }
    /* Make Streamlit input look cleaner */
    div[data-testid="stChatInput"] {
        padding: 0;
        border: 1px solid #e0e0e0;
        border-radius: 24px;
        background: white;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #4e54c8;
        box-shadow: 0 0 0 2px rgba(78, 84, 200, 0.2);
    }

    /* --- Floating Action Button (FAB) --- */
    .fab-button {
        width: 60px; height: 60px; border-radius: 50%;
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 28px; cursor: pointer;
        box-shadow: 0 8px 20px rgba(78, 84, 200, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: none;
    }
    .fab-button:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 25px rgba(78, 84, 200, 0.6);
    }
    
    /* Hide default streamlit deploy button if it overlaps */
    header[data-testid="stHeader"] { z-index: 9998; }
    </style>
    """, unsafe_allow_html=True)

def render_floating_chatbot():
    """Main function to render the floating AI assistant."""
    
    # Initialize session states
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        # System prompt tailored for your Supply Chain system
        system_prompt = {
            "role": "system",
            "content": """You are the AI Supply Chain Assistant for a multi-role logistics platform. 
            You help Producers with inventory and pricing, Merchants with orders and matching, 
            Customers with tracking, and Admins with system insights. 
            Be professional, concise, and highly knowledgeable about supply chain operations."""
        }
        st.session_state.chat_messages = [system_prompt]

    inject_chatbot_styles()

    # Create the floating container
    float_container = st.container()
    float_container.float("bottom: 2rem; right: 2rem; z-index: 9999;")

    with float_container:
        if st.session_state.chat_open:
            # --- CHAT WINDOW UI ---
            st.markdown('<div class="chat-widget-container">', unsafe_allow_html=True)
            
            # Header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("""
                <div class="chat-header">
                    <div class="chat-header-info">
                        <div class="chat-avatar">🤖</div>
                        <div>
                            <p class="chat-title">Supply Chain AI</p>
                            <p class="chat-subtitle">● Online | Powered by Groq</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✕", key="close_chat", help="Close Chat"):
                    st.session_state.chat_open = False
                    st.rerun()

            # Messages Area
            with st.container():
                st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
                # Display history (skip system prompt)
                for message in st.session_state.chat_messages[1:]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                st.markdown('</div>', unsafe_allow_html=True)

            # Input Area
            with st.container():
                st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
                prompt = st.chat_input("Ask about inventory, orders, or pricing...", key="chat_input")
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True) # Close widget container

            # Handle user input
            if prompt:
                # Add user message
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        client = init_groq_client()
                        if client:
                            try:
                                stream = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=st.session_state.chat_messages,
                                    temperature=0.7,
                                    max_tokens=1024,
                                    stream=True,
                                )
                                response = st.write_stream(stream)
                                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                            except Exception as e:
                                st.error(f"Error connecting to Groq: {e}")
        else:
            # --- FLOATING ACTION BUTTON (FAB) UI ---
            if st.button("💬", key="open_chat", help="Open AI Assistant"):
                st.session_state.chat_open = True
                st.rerun()
            
            # Apply FAB styling via a hacky but effective markdown wrapper
            st.markdown("""
            <style>
            button[kind="secondary"][data-testid="baseButton-secondary"]:has(> div[data-testid="stMarkdownContainer"] > p) {
                /* This targets the button if needed, but we use the class defined above */
            }
            </style>
            """, unsafe_allow_html=True)
