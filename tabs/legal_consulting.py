#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:10:58 2025

@author: amna

"""
import streamlit as st

SYSTEM_PROMPT = """You are a legal expert trained in Pakistani family law…"""

def render(client):
    tab_name = "Legal Consulting"
    # initialize history
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # display past messages
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # chat input
    if prompt := st.chat_input("Ask your legal question…"):
        st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state.openai_model,
                messages=st.session_state.messages[tab_name],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages[tab_name].append({"role": "assistant", "content": response})
