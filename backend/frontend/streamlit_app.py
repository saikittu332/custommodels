import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.title("Custom AI Bots Demo — Tech IT Support & Health Clinic FAQ")

if "messages" not in st.session_state:
    st.session_state.messages = []

client = st.selectbox(
    "Choose AI Bot (Client)",
    options=["client1", "client2"],
    format_func=lambda x: "Tech Company IT Support Bot" if x == "client1" else "Health Clinic FAQ Bot"
)

def send_question(client_id, question):
    try:
        response = requests.post(f"{API_URL}/ask/", json={"client_id": client_id, "question": question})
        if response.status_code == 200:
            return response.json().get("answer", "No answer received.")
        else:
            return "Error from backend: " + response.text
    except Exception as e:
        return f"API request failed: {e}"

with st.chat_input("Ask your question here...") as user_question:
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question, "client": client})
        answer = send_question(client, user_question)
        st.session_state.messages.append({"role": "assistant", "content": answer, "client": client})

for msg in st.session_state.messages:
    if msg["client"] == client:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
