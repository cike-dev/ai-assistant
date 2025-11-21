
import streamlit as st
import requests
from datetime import datetime

# Page setup
st.set_page_config(
    page_title="Wolvina Assistant",
    page_icon="💬",
    layout="wide"
)

# WhatsApp-style CSS
st.markdown("""
<style>

    :root {
        --user-bg: #0c0c0c;          /* Dark green for user bubbles */
        --bot-bg: #202c33;           /* Dark gray for bot bubbles */
        --timestamp: #8696a0;        /* Light gray for timestamps */
        --shadow: rgba(0, 0, 0, 0.4);
        --text-light: #e9edef;       /* Light text for dark bubbles */
    }

     body {
        background-color: #0b141a;   /* Dark background */
        background-image: none;       /* Remove pattern if needed */

        /* background-image: url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M13 13h6v6h-6v-6zm10 10h6v6h-6v-6zm10 10h6v6h-6v-6zm0-10h6v6h-6v-6zm0-10h6v6h-6v-6z' fill='%23dddbd6' fill-opacity='0.2' fill-rule='evenodd'/%3E%3C/svg%3E"); */
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    }

    .stApp {
        background-color: transparent !important;
        max-width: 800px;
        margin: 0 auto;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
            
        padding-bottom: 80px;  /* Space for fixed input */
        box-sizing: border-box;
    }

    .chat-container {
        height: calc(100vh - 180px); /* Adjust height to account for fixed input */
        overflow-y: auto;
        padding: 20px 10px 100px;
        background-color: #0b141a;
        position: relative;
        display: flex;
        flex-direction: column;
    }

    .message-group {
        display: flex;
        flex-direction: column;
        max-width: 70%;
        /* width: 100%; */
        margin: 4px 0;
        align-items: flex-start;
        /* box-sizing: border-box; */
    }

    .user-group {
        align-self: flex-end;
        align-items: flex-end;
    }

    .message {
        padding: 8px 12px;
        border-radius: 7.5px;
        position: relative;
        word-wrap: break-word;
        white-space: pre-wrap;
        word-break: break-word;
            
        min-width: 40px;
        max-width: 90%;
        box-shadow: 0 1px 0.5px var(--shadow);
        animation: fadeIn 0.3s;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .bot-message {
        background-color: var(--bot-bg);
        color: var(--text-light);    /* Light text for bot messages */
        border-top-left-radius: 0;
        margin-right: auto;
    }

    .user-message {
        background-color: var(--user-bg);
        color: var(--text-light);    /* Light text for user messages */
        border-top-right-radius: 0;
        margin-left: auto;
    }

    .timestamp {
        font-size: 0.65rem;
        color: var(--timestamp);     /* Adjusted for dark background */        color: var(--timestamp);
        margin: 2px 8px;
        align-self: flex-end;
        white-space: nowrap;
    }

    .button-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
        justify-content: flex-start;
    }

    .stButton>button {
        font-size: 0.85rem;
        padding: 6px 12px;
        background-color: #1f2c33 !important;
        color: #00a884 !important;   /* WhatsApp green for buttons */        color: #075e54;
        border: 1px solid #8696a0 !important;
        border-radius: 18px;
        margin: 2px;
        transition: all 0.2s;
        box-shadow: none;
    }

    .stButton>button:hover {
        background-color: #2a3942 !important;
        border-color: #075e54;
        color: #25d366 !important;   /* Brighter green on hover */
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /*
        .input-container {
            position: fixed;
            bottom: 20px;
            width: 100%;
            background: transparent;
            padding: 10px;
            max-width: 780px;
        }
    */
    
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0b141a;
        padding: 15px;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.15);
        z-index: 100;
    }

    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }

    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }

    /* Dark text input */
    .stTextInput>div>div>input {
        color: white !important;
        background-color: #2a3942 !important;
        border: 1px solid #8696a0 !important;
    }
            

    .chat-messages {
        max-height: calc(100vh - 150px);
        overflow-y: auto;
        padding-bottom: 20px;
        display: flex;
        flex-direction: column-reverse; /* New messages stick to bottom */
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    st.session_state.button_clicked = False
    st.session_state.pending_button_payload = None

# Header section
st.header("💬 WhatsApp-Style Chat Assistant")
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
        # Add this wrapper div around your chat messages
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            # Wrap each message in a group container
            group_class = "user-group" if message["role"] == "user" else ""

            st.markdown(f'<div class="message-group {group_class}">', unsafe_allow_html=True)

            # Display the message content
            bubble_class = "user-message" if message["role"] == "user" else "bot-message"
            st.markdown(f'<div class="message {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

            # Display timestamp
            st.markdown(f'<div class="timestamp">{message["time"]}</div>', unsafe_allow_html=True)

            # Display buttons if they exist
            if "buttons" in message and message["buttons"]:
                with st.container():
                    button_container = st.columns(min(3, len(message["buttons"])))
                    for i, btn in enumerate(message["buttons"]):
                        with button_container[i % len(button_container)]:
                            st.button(
                                btn['title'], 
                                key=f"btn_{message['time']}_{i}",
                                on_click=handle_button_click,
                                args=(btn['payload'], btn['title'])
                            )

            # st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # st.markdown("""
    #     <script>
    #         // Auto-scroll to newest messages
    #         const container = document.querySelector('.chat-messages');
    #         if(container) container.scrollTop = container.scrollHeight;
    #     </script>
    # """, unsafe_allow_html=True)

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
            placeholder="Type a message...",
            label_visibility="collapsed"
        )
    with cols[1]:
        submitted = st.form_submit_button("➤")

if (user_input and submitted) or (user_input and not submitted):
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "time": timestamp
    })
    
    # Get and display Rasa response
    with st.spinner(""):
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


# JavaScript script to auto-scroll to new messages
st.markdown("""
<script>
    // Auto-scroll to latest message
    function scrollToBottom() {
        const container = document.querySelector('.chat-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    // Run on load and after every Streamlit event
    window.addEventListener('load', scrollToBottom);
    document.addEventListener('DOMContentLoaded', scrollToBottom);
    window.addEventListener('resize', scrollToBottom);

    // Mutation observer to detect new messages
    const observer = new MutationObserver(scrollToBottom);
    const targetNode = document.querySelector('.chat-container');
    if (targetNode) {
        observer.observe(targetNode, {childList: true, subtree: true});
    }
</script>
""", unsafe_allow_html=True)    


