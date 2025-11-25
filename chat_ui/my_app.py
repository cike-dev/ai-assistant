import streamlit as st
import requests
import uuid

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sender_id' not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())

# Streamlit UI
st.title("My Rasa Chatbot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to send message to Rasa server
def send_message_to_rasa(message):
    RASA_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
    json_payload = {
        "sender": st.session_state.sender_id,
        "message": message
    }
    response = requests.post(RASA_ENDPOINT, json=json_payload)
    return response.json()

# User input
if user_input := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Send message to Rasa and get response
    bot_messages = send_message_to_rasa(user_input)
    
    # # Get bot responses
    # bot_messages = response.json()
    
    # Display bot responses
    for msg in bot_messages:
        bot_text = msg.get("text", "")
        buttons = msg.get("buttons", [])

        # Add to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_text,
            "buttons": buttons})
        
        # Display bot message
        with st.chat_message("assistant"):
            st.write(bot_text)
        
        if buttons:
            with st.form(key=f"button_form_{len(st.session_state.messages)}"):
                # 1. Selectbox is now inside the form
                button_choice = st.selectbox(
                    "Choose an option:",
                    options=[btn["title"] for btn in buttons],
                    # Do NOT use a unique key here; let the form handle it
                )
                
                # 2. Use the dedicated form submit button
                submitted = st.form_submit_button("Send Choice")

                if submitted:
                    # 3. All processing happens *only* if the button is clicked
                    
                    # Find the selected button's payload
                    selected_button = next(btn for btn in buttons if btn["title"] == button_choice)
                    
                    # Add user's selected choice to history
                    st.session_state.messages.append({"role": "user", "content": button_choice}) 

                    # Send payload to Rasa and get new response
                    new_bot_messages = send_message_to_rasa(selected_button["payload"])
                    
                    # Add the new bot message(s) to history
                    for msg in new_bot_messages:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": msg.get("text", "")
                        })
                    
                    # Force a full rerun to update the chat history cleanly
                    st.experimental_rerun()

        # # Display buttons as selectbox instead
        # if buttons:
        #     button_choice = st.selectbox(
        #         "Choose an option:",
        #         options=[btn["title"] for btn in buttons],
        #         key=f"select_{len(st.session_state.messages)}"
        #     )
            
        #     if st.button("Send", key=f"send_{len(st.session_state.messages)}"):
        #         # Find the selected button's payload
        #         selected_button = next(btn for btn in buttons if btn["title"] == button_choice)

        #         # Add selected button title (user's action) to history
        #         st.session_state.messages.append({"role": "user", "content": button_choice})
                
        #         # Send payload to Rasa and get new response
        #         new_bot_messages = send_message_to_rasa(selected_button["payload"])

        #         # Process and display the new bot messages
        #         for msg in new_bot_messages:
        #             # Add to history
        #             st.session_state.messages.append({
        #                 "role": "assistant", 
        #                 "content": msg.get("text", "")
        #             })

        #             # Rerun Streamlit to update the chat history
        #             st.experimental_rerun()

        # # Display buttons as separate buttons if any
        # if buttons:
        #     cols = st.columns(len(buttons))
        #     for idx, button in enumerate(buttons):
        #         with cols[idx]:
        #             if st.button(button["title"], key=f"btn_{len(st.session_state.messages)}_{idx}"):
        #                 # When button is clicked, send the payload to Rasa
        #                 button_response = send_message_to_rasa(button["payload"])

        #                 # Add button click to history (as user message)
        #                 st.session_state.messages.append({
        #                     "role": "user",
        #                     "content": button["payload"]
        #                 })

        #                 # Display bot's response to button click
        #                 for response_msg in button_response:
        #                     response_text = response_msg.get("text", "")
        #                     st.session_state.messages.append({
        #                         "role": "assistant",
        #                         "content": response_text,
        #                     })

        #                 # Rerun the app to show updated messages
        #                 st.experimental_rerun()
                            
        #                     # with st.chat_message("assistant"):
        #                     #     st.write(response_text)

