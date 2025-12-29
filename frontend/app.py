import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/rag/query"

st.title("RAG Chatbot")

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
            r = requests.post(API_URL, json={"question": user_q}, timeout=60)
            r.raise_for_status()
            answer = r.json()["answer"]
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
