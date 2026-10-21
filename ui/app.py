"""Step 3b: Streamlit chat UI that talks to the API.

Run the API first:   uvicorn app.api:app --port 8000
Then the UI:         streamlit run ui/app.py
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Agentic RAG Assistant", page_icon="📚")
st.title("📚 Agentic RAG Assistant")
st.caption("Answers come only from your documents, with sources. Runs locally with Llama 3.2.")


def api_is_up() -> bool:
    try:
        return requests.get(f"{API_URL}/health", timeout=2).ok
    except requests.RequestException:
        return False


with st.sidebar:
    st.subheader("Status")
    if api_is_up():
        st.success("API connected")
    else:
        st.error(f"API not reachable at {API_URL}")
        st.code("uvicorn app.api:app --port 8000")
    st.subheader("Try asking")
    st.markdown("- How does a solar cell work?\n- What is the Betz limit?\n- what is 17 * 23 + 5?")
    if st.button("Clear chat"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []


def show_meta(msg: dict) -> None:
    if msg.get("sources"):
        st.caption("Sources: " + ", ".join(msg["sources"]))
    if msg.get("route"):
        st.caption(f"Route: {msg['route']}")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        show_meta(msg)

if question := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=300)
                if r.ok:
                    data = r.json()
                    msg = {"role": "assistant", "content": data["answer"],
                           "sources": data["sources"], "route": data["route"]}
                else:
                    msg = {"role": "assistant", "content": f"⚠️ {r.json().get('detail', r.text)}"}
            except requests.RequestException as e:
                msg = {"role": "assistant", "content": f"⚠️ Could not reach the API: {e}"}
        st.markdown(msg["content"])
        show_meta(msg)
    st.session_state.messages.append(msg)
