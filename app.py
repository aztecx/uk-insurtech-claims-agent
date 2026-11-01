import os
import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="UK InsurTech Claims Agent",
    layout="centered"
)

# App Header
st.title("UK InsurTech Claims & Reconciliation Agent")
st.markdown("An autonomous AI agent powered by **FastMCP**, **Ollama (qwen2.5:3b)**, and **FastAPI** to verify policies, calculate deductibles, and process payouts.")

# FastAPI Backend URL
# Fallback to localhost for local runs, or use container networking inside Docker
API_URL = os.getenv("API_URL", "http://localhost:8000/claims/process")

# Initialize Chat History in Streamlit Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Prior Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Describe your insurance claim (e.g., 'I need to file a claim for POL-UK-0001, repair cost is £1200')"):
    # Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send request to FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning, verifying policy, and checking tools..."):
            try:
                response = requests.post(API_URL, json={"claim_text": prompt})
                if response.status_code == 200:
                    data = response.json()
                    agent_reply = data.get("response", "No response received.")
                else:
                    agent_reply = f"Error from backend: {response.text}"
            except requests.exceptions.ConnectionError:
                agent_reply = "Error: Could not connect to the FastAPI backend. Make sure `main.py` is running!"
            
            st.markdown(agent_reply)
            
    # Save assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": agent_reply})