import streamlit as st
import requests
import uuid

# Initialize session state for conversation history and button handling
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'sender_id' not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())

if 'awaiting_button_response' not in st.session_state:
    st.session_state.awaiting_button_response = False

if 'current_buttons' not in st.session_state:
    st.session_state.current_buttons = []

if 'session_started' not in st.session_state:
    st.session_state.session_started = False

# --------------------- Show App title -------------------------- #
# Streamlit UI
st.title("Golden Prime")

# --------------------------------------------------------- #
# ------ Helper function that sends/receives messages ----- #
# ----------- to/from the server's API Endpoint ----------- #

# Function to send message to Rasa server
def send_message_to_rasa(message, metadata=None):
    payload = {
        "sender": st.session_state.sender_id,
        "message": message
    }
    if metadata:
        payload["metadata"] = metadata

    RASA_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"

    json_payload = {
        "sender": st.session_state.sender_id,
        "message": message
    }

    response = requests.post(RASA_ENDPOINT, json=json_payload)
    return response.json()



# Start session on first load
if not st.session_state.session_started:
    # Send /session_start to trigger pattern_session_start
    bot_messages = send_message_to_rasa(
        "/session_start",
        metadata={"source": "streamlit", "user_agent": "web"}
    )
    
    # Process the greeting message response
    for msg in bot_messages:
        bot_text = msg.get("text", "")
        buttons = msg.get("buttons", [])
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_text
        })
        
        if buttons:
            st.session_state.current_buttons = buttons
            st.session_state.awaiting_button_response = True
    
    st.session_state.session_started = True
    st.rerun()


# -------------------------------------------------------- #
# ----------------- Display chat history ----------------- # 

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# ----------------------------------------------- #
# ----------- Handle button responses ----------- #

# Show buttons if we're waiting for a button response
if st.session_state.awaiting_button_response and st.session_state.current_buttons:
    # st.write("**Choose an option:**")

    # Create columns for buttons
    cols = st.columns(len(st.session_state.current_buttons))
    
    for idx, button in enumerate(st.session_state.current_buttons):
        with cols[idx]:
            if st.button(button["title"], key=f"btn_{idx}"):
                # Add user's choice to chat history (show the title, not payload)
                st.session_state.messages.append({
                    "role": "user",
                    "content": button["title"]
                })
                
                # Send the payload to Rasa
                bot_messages = send_message_to_rasa(button["payload"])

    
    # ---- uncomment below to use selectbox approach ---- #

    # # ======== Using Selectbox to handle buttons (alternative approach) ========
    # # Show selectbox if we have buttons
    # selected_title = st.selectbox(
    #     "Choose an option:",
    #     options=[btn["title"] for btn in st.session_state.current_buttons],
    #     key="button_select"
    # )
    
    # if st.button("Send Choice", key="send_choice"):
    #     # Find the payload for the selected title
    #     selected_button = next(
    #         btn for btn in st.session_state.current_buttons 
    #         if btn["title"] == selected_title
    #     )
        
    #     # Add user's choice to history
    #     st.session_state.messages.append({
    #         "role": "user",
    #         "content": selected_title
    #     })
        
    #     # Send payload to Rasa
    #     bot_messages = send_message_to_rasa(selected_button["payload"])

        # If using the selectbox approach, move the for-loop below
        # to this indentation level

                # Process bot responses
                for msg in bot_messages:
                    bot_text = msg.get("text", "")
                    new_buttons = msg.get("buttons", [])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_text
                    })
                    
                    # Update button state
                    if new_buttons:
                        st.session_state.current_buttons = new_buttons
                        st.session_state.awaiting_button_response = True
                    else:
                        st.session_state.current_buttons = []
                        st.session_state.awaiting_button_response = False
                
                st.rerun()

# ----------------------------------------------- #

# Regular text input (only show if not waiting for button response)
if not st.session_state.awaiting_button_response:
    if user_input := st.chat_input("Type your message here..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Send to Rasa
        bot_messages = send_message_to_rasa(user_input)
        
        # Process bot responses
        for msg in bot_messages:
            bot_text = msg.get("text", "")
            buttons = msg.get("buttons", [])
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_text
            })
            
            # If there are buttons, set up button state
            if buttons:
                st.session_state.current_buttons = buttons
                st.session_state.awaiting_button_response = True
        
        st.rerun()
