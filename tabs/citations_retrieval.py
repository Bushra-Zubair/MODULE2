#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:14:37 2025

@author: amna
"""

# tabs/citations_retrieval.py
import streamlit as st

SYSTEM_PROMPT = """You are an expert in Pakistani legal research. Provide relevant statutes, case law citations, and brief summaries based on user queries, formatted clearly."""

def render(client):
    tab_name = "Citations Retrieval"
    # Initialize message history for this tab
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Query input
    query = st.text_input("Enter Topic or Keyword for Citations")
    if st.button("Retrieve Citations"):
        prompt = f"Provide relevant Pakistani statutes, sections, and landmark case citations with brief summaries for: {query}"
        st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
        # Stream response
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state.openai_model,
                messages=st.session_state.messages[tab_name],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages[tab_name].append({"role": "assistant", "content": response})
