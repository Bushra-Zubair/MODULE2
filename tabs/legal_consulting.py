#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legal Consulting Tab for Wakeel App

This module provides a chat interface for users to ask questions related
to Pakistani family and civil law. It leverages a fine-tuned OpenAI model
and provides answers in both English and Urdu.

Created on Wed May 14 15:10:58 2025
@author: amna
"""

import streamlit as st

# Finetuned model (can be set in session or overridden)
DEFAULT_MODEL = "ft:gpt-4o-2024-08-06:iml-research:wakeel:BW4oryHJ"

# System prompt defining assistant behavior
SYSTEM_PROMPT = """You are a legal expert trained in Pakistani family and civil law. Your role is to explain the answer in both clear English and simple Urdu so that it is understandable by both lawyers and the general public.

1. The tone should be:
   - Clear and professional (for law students)
   - Simple and respectful (for general users)
2. Structure your response in two parts:
   - **English Explanation**
   - ** اردو وضاحت**
3. Keep the total response under 250 words for each language, 500 for both.
4. Avoid legal jargon unless necessary. If used, explain it clearly.
### Ask user if they want to ask more questions

### If a query is unrelated to Pakistani family law (e.g., criminal law, international law, general legal advice), politely refuse to answer and remind the user of your domain restriction.
### Focus areas include: divorce, child custody, maintenance (nafaqah), polygamy, nikah, dissolution of marriage, guardianship, inheritance under family law, and related topics.

Now generate a response that answers the user's question."""

def setup_session_state(tab_name: str):
    """Initializes model and message history in session state."""
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = DEFAULT_MODEL

    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

def display_chat_history(tab_name: str):
    """Displays all user and assistant messages."""
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

def handle_user_prompt(client, tab_name: str):
    """Processes the user's legal question and generates a response."""
    if prompt := st.chat_input("Ask your legal question…"):
        # Append user message
        st.session_state.messages[tab_name].append({"role": "user", "content": prompt})

        # Stream assistant response
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages[tab_name],
                    stream=True,
                )
                response = st.write_stream(stream)
            except Exception as e:
                response = f"⚠️ An error occurred: {e}"
                st.error(response)

        # Append assistant message
        st.session_state.messages[tab_name].append({"role": "assistant", "content": response})

def render(client):
    """Main render function for the Legal Consulting tab."""
    tab_name = "Legal Consulting"
    st.header("Legal Consulting | قانونی مشورہ 👩🏻‍⚖️📚𓍝🏛️🖋️")

    setup_session_state(tab_name)
    display_chat_history(tab_name)
    handle_user_prompt(client, tab_name)
