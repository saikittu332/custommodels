import streamlit as st
import requests

# Backend config
API_URL = "http://localhost:8000"
st.set_page_config(page_title="Custom AI Bots", layout="centered")

# App title and bot selector
st.title("Custom AI Bots — Tech & Health")

client = st.selectbox(
    "Select a Bot",
    options=["client1", "client2"],
    format_func=lambda x: "Tech Company IT Support Bot" if x == "client1" else "Health Clinic FAQ Bot"
)

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Backend call function
def send_question(client_id, question):
    try:
        response = requests.post(f"{API_URL}/ask/", json={"client_id": client_id, "question": question})
        if response.status_code == 200:
            return response.json().get("answer", "No answer received.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API request failed: {e}"

# Display chat messages for the selected client
st.divider()
for msg in st.session_state.messages:
    if msg["client"] == client:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Compact file uploader (optional)
with st.container():
    uploaded_file = st.file_uploader("Upload a file (optional)", type=None, label_visibility="collapsed")
    if uploaded_file:
        # Streamlit versions may not implement `st.toast`; use `st.success` which is widely supported.
        st.success(f"📎 File uploaded: {uploaded_file.name}")

# Chat input at the bottom (always at root)
user_input = st.chat_input("Type your question here...")

# Process user input
if user_input:
    # Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "client": client
    })

    # Call backend
    bot_reply = send_question(client, user_input)

    # Append assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "client": client
    })

    # Display messages immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
