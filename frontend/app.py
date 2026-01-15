import os
import streamlit as st
import requests

# Default: FastAPI local
API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8001/rag/query")

st.title("RAG Chatbot")

st.caption(f"API: {API_URL}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_q = st.chat_input("Ask a question about the documents...")

if user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(API_URL, json={"question": user_q}, timeout=60)
                r.raise_for_status()
                answer = r.json().get("answer", "")
                if not answer:
                    answer = "No answer returned from API."
                st.markdown(answer)
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach API at {API_URL}. Is the backend running?\n\nDetails: {e}")
                answer = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
