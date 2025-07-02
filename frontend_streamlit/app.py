import streamlit as st
import requests
from typing import List, Dict

st.set_page_config(page_title="Invoice Status Chatbot", page_icon="🧾", layout="centered")
st.title("🧾 Invoice Status Chatbot")
st.markdown("""
Welcome to the multi-lingual Invoice Status Chatbot! Ask about your PO or Non-PO (ACR) invoices. The assistant supports tables, rich text, emoji, and images. If you need help, just ask!
""")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

user_input = st.chat_input("Type your invoice query here...")

backend_url = st.secrets["BACKEND_URL"] if "BACKEND_URL" in st.secrets else "http://localhost:8000/api/chat"

def render_message(msg: Dict):
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

def call_backend(messages: List[Dict]):
    try:
        response = requests.post(backend_url, json={"messages": messages}, timeout=30)
        response.raise_for_status()
        return response.json()["reply"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

for msg in st.session_state['messages']:
    render_message(msg)

if user_input:
    st.session_state['messages'].append({"role": "user", "content": user_input})
    with st.spinner("Assistant is typing..."):
        reply = call_backend(st.session_state['messages'])
    st.session_state['messages'].append({"role": "assistant", "content": reply})
    render_message({"role": "assistant", "content": reply}) 