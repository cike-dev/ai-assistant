import streamlit as st
import requests
from datetime import datetime
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from custom_logger import get_logger
logger = get_logger("ChatUI")

# Page setup
st.set_page_config(
    page_title="Wolvina Assistant",
    page_icon="💬",
    layout="wide"
)


def load_css(file_name):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(script_dir, file_name)
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        logger.info(f"Successfully loaded CSS from {css_path}")
    except FileNotFoundError:
        logger.error(f"CSS file not found at {css_path}")
        # Fallback: use embedded CSS
        # load_fallback_css()

  

# Load CSS file
load_css('styles_1.css')

st.markdown('<div class="chat-ui">', unsafe_allow_html=True)


#  session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    st.session_state.button_clicked = False
    st.session_state.pending_button_payload = None

# Header section
st.header("💬 Wolvina Assistant")
st.caption("Powered by Rasa Open Source • Messages are end-to-end encrypted 🔒")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    st.session_state.rasa_url = st.text_input(
        "Rasa Server URL",
        value=st.session_state.rasa_url,
        help="Endpoint format: http://<host>:<port>/webhooks/rest/webhook"
    )
    
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Start Rasa server with `rasa run`\n2. Verify endpoint URL\n3. Type your message below")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("**Connection Status:**")
    try:
        response = requests.get(st.session_state.rasa_url.replace("/webhooks/rest/webhook", ""), timeout=2)
        if response.status_code == 200:
            st.success("Connected to Rasa server")
        else:
            st.warning(f"Server returned {response.status_code}")
    except:
        st.error("Unable to connect to server")

# Function to get Rasa response
def get_rasa_response(message, sender="user"):
    payload = {
        "sender": sender,
        "message": message
    }
    
    try:
        response = requests.post(
            st.session_state.rasa_url,
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return [{"text": f"Error: Rasa server returned {response.status_code}"}]
    except Exception as e:
        return [{"text": f"Connection error: {str(e)}"}]

# Function to handle button clicks
def handle_button_click(button_payload, button_title):
    st.session_state.button_clicked = True
    st.session_state.pending_button_payload = button_payload
    st.session_state.pending_button_title = button_title

# Main chat container
chat_container = st.container()
with chat_container:
    # Messages display
    container = st.container()
    with container:
        # === Chat Scroll Area ===
        st.markdown('<div class="chat-scroll-area">', unsafe_allow_html=True)

        for message in reversed(st.session_state.messages):  # newest at bottom
            group_class = "user-group" if message["role"] == "user" else ""
            st.markdown(f'<div class="message-group {group_class}">', unsafe_allow_html=True)

            bubble_class = "user-message" if message["role"] == "user" else "bot-message"
            st.markdown(f'<div class="message {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

            timestamp_style = "text-align: right;" if message["role"] == "user" else "text-align: left;"
            st.markdown(f'<div class="timestamp" style="{timestamp_style}">{message["time"]}</div>', unsafe_allow_html=True)

            # ✅ Render Rasa buttons for bot messages
            if message["role"] == "assistant" and "buttons" in message and message["buttons"]:
                st.markdown('<div class="button-container">', unsafe_allow_html=True)
                cols = st.columns(min(3, len(message["buttons"])))
                for i, btn in enumerate(message["buttons"]):
                    with cols[i % len(cols)]:
                        st.button(
                            btn['title'],
                            key=f"btn_{message['time']}_{i}_{hash(btn['title'])}",
                            on_click=handle_button_click,
                            args=(btn['payload'], btn['title'])
                        )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        

    
# Handle button click processing
if st.session_state.button_clicked and st.session_state.pending_button_payload:
    # Add user message for the button click
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": st.session_state.pending_button_title,
        "time": timestamp
    })
    
    # Get response from Rasa for the button payload
    with st.spinner(""):
        responses = get_rasa_response(st.session_state.pending_button_payload)
    
    if responses:
        for response in responses:
            bot_message = response.get('text', 'No response text')
            buttons = response.get('buttons', [])
            timestamp = datetime.now().strftime("%H:%M")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_message,
                "time": timestamp,
                "buttons": buttons
            })
    
    # Reset button state
    st.session_state.button_clicked = False
    st.session_state.pending_button_payload = None
    st.session_state.pending_button_title = None
    st.rerun()

# Message input area at bottom
with st.form(key='message_form', clear_on_submit=True):
    cols = st.columns([10, 1])
    with cols[0]:
        user_input = st.text_input(
            "Type a message", 
            "", 
            key="input",
            placeholder="  Type a message...",
            label_visibility="collapsed"
        )
    with cols[1]:
        submitted = st.form_submit_button("➤")
st.markdown('</div>', unsafe_allow_html=True)


if submitted and user_input:  # Only process when form is actually submitted
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "time": timestamp
    })
     
    # Get and display Rasa response
    with st.spinner("thinking..."):
        responses = get_rasa_response(user_input)
    
    if responses:
        for response in responses:
            bot_message = response.get('text', 'No response text')
            buttons = response.get('buttons', [])
            timestamp = datetime.now().strftime("%H:%M")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_message,
                "time": timestamp,
                "buttons": buttons
            })
    
    st.rerun()


# Replace your current JavaScript with:
st.markdown("""
<script>
    function scrollToBottom() {
        const container = document.querySelector('[data-testid="stContainer"]');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
        
        // Alternative selectors
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Multiple strategies to ensure scrolling works
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 500);
    
    // Observe for changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setTimeout(scrollToBottom, 100);
            }
        });
    });
    
    // Start observing
    const targetNode = document.querySelector('.stApp') || document.body;
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
    
    // Also scroll on window load
    window.addEventListener('load', scrollToBottom);
</script>
""", unsafe_allow_html=True)
