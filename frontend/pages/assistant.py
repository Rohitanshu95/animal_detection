"""
AI Assistant Page
Conversational AI for wildlife incident analysis
"""

import streamlit as st
import requests
from datetime import datetime
import json


# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Backend API URL
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if 'assistant_messages' not in st.session_state:
    st.session_state.assistant_messages = []

if 'show_tool_calls' not in st.session_state:
    st.session_state.show_tool_calls = False


# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 20%;
    }
    .message-role {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .tool-call {
        background-color: #FFF3E0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        border-left: 3px solid #FF9800;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 AI Assistant")
st.markdown("Ask questions about wildlife incidents, analyze patterns, and get insights from the data.")

# Sidebar with features and examples
with st.sidebar:
    st.markdown("### 🎯 What I Can Do")
    st.markdown("""
    - **Search incidents** by any criteria
    - **Analyze trends** over time
    - **Find patterns** in the data
    - **Compare statistics** across regions
    - **Answer questions** about specific incidents
    - **Provide insights** and recommendations
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    
    examples = [
        "What are the most common types of wildlife being smuggled?",
        "Show me incidents from the last 30 days",
        "Which locations have the highest number of incidents?",
        "What are the current trends in elephant poaching?",
        "Find incidents similar to ivory trafficking",
        "Compare incidents between regions",
        "What's the average quantity seized per incident?",
        "Show me all cases under investigation"
    ]
    
    for example in examples:
        if st.button(f"💬 {example}", key=example, use_container_width=True):
            st.session_state.assistant_messages.append({
                "role": "user",
                "content": example,
                "timestamp": datetime.now().isoformat()
            })
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    st.session_state.show_tool_calls = st.checkbox(
        "Show tool usage",
        value=st.session_state.show_tool_calls,
        help="Display which tools the assistant uses to answer your questions"
    )
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.assistant_messages = []
        st.rerun()

# Main chat interface
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.assistant_messages:
        role = message.get('role', 'user')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        
        if role == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-role">👤 You</div>
                <div>{content}</div>
                <div class="timestamp">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # assistant
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-role">🤖 Assistant</div>
                <div>{content}</div>
            """, unsafe_allow_html=True)
            
            # Show tool calls if enabled
            if st.session_state.show_tool_calls and message.get('tool_calls'):
                for tool_call in message['tool_calls']:
                    st.markdown(f"""
                    <div class="tool-call">
                        <strong>🔧 Tool:</strong> {tool_call.get('tool', 'unknown')}<br>
                        <strong>📥 Input:</strong> {tool_call.get('input', 'N/A')}<br>
                        <strong>📤 Output:</strong> {tool_call.get('output', 'N/A')[:200]}...
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="timestamp">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "Ask me anything about wildlife incidents...",
        key="user_input",
        placeholder="e.g., What are the top 5 animals being smuggled?"
    )

with col2:
    send_button = st.button("Send 📤", type="primary", use_container_width=True)

# Process new message
if (send_button or user_input) and user_input:
    # Add user message
    st.session_state.assistant_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Show thinking indicator
    with st.spinner("🤔 Thinking..."):
        try:
            # Prepare chat history (exclude current message)
            chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.assistant_messages[:-1]
            ]
            
            # Call backend
            response = requests.post(
                f"{API_BASE_URL}/assistant/chat",
                json={
                    "message": user_input,
                    "chat_history": chat_history
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add assistant response
                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": result.get("message", "I couldn't generate a response."),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tool_calls": result.get("tool_calls", [])
                })
            else:
                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: Could not get response from server (Status: {response.status_code})",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
        except Exception as e:
            st.session_state.assistant_messages.append({
                "role": "assistant",
                "content": f"❌ Error: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Clear input and rerun
    st.rerun()

# Quick stats footer
if len(st.session_state.assistant_messages) > 0:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Messages", len(st.session_state.assistant_messages))
    with col2:
        user_msgs = sum(1 for m in st.session_state.assistant_messages if m['role'] == 'user')
        st.metric("Your Questions", user_msgs)
    with col3:
        assistant_msgs = sum(1 for m in st.session_state.assistant_messages if m['role'] == 'assistant')
        st.metric("Responses", assistant_msgs)
else:
    # Welcome message for new users
    st.info("""
    👋 **Welcome to the AI Assistant!**
    
    I'm here to help you analyze wildlife smuggling incidents. You can:
    - Ask me questions in natural language
    - Request specific data searches
    - Get statistical insights
    - Analyze trends and patterns
    
    Try asking me something from the sidebar examples, or type your own question!
    """)
