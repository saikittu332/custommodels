import streamlit as st
import requests

# You can hardcode your backend API URL or get from secrets
API_URL = "http://localhost:8000"
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")

st.title("Custom AI Bots Demo — Tech IT Support & Health Clinic")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Select client bot
client = st.selectbox(
    "Choose AI Bot (Client)",
    options=["client1", "client2"],
    format_func=lambda x: "Tech Company IT Support Bot" if x == "client1" else "Health Clinic FAQ Bot"
)

def send_question(client_id, question):
    """Call backend API to get AI answer"""
    try:
        response = requests.post(f"{API_URL}/ask/", json={"client_id": client_id, "question": question})
        if response.status_code == 200:
            return response.json().get("answer", "No answer received.")
        else:
            return "Error from backend: " + response.text
    except Exception as e:
        return f"API request failed: {e}"

# Display existing messages for chosen client
for msg in st.session_state.messages:
    if msg["client"] == client:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Accept user input with chat_input (do NOT use `with` here)
user_question = st.chat_input("Ask your question here...")

if user_question:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question, "client": client})
    
    # Get response from backend
    answer = send_question(client, user_question)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer, "client": client})
    
    # Display the user message and assistant answer immediately
    with st.chat_message("user"):
        st.markdown(user_question)
    with st.chat_message("assistant"):
        st.markdown(answer)
