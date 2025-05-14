#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:14:28 2025

@author: amna
"""

# tabs/petition_drafting.py
import streamlit as st

SYSTEM_PROMPT = """You are a seasoned Pakistani family law practitioner. Draft clear, concise legal petitions based on user-provided case details, following Pakistani court conventions."""

def render(client):
    tab_name = "Petition Drafting"
    # Initialize message history for this tab
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Collect petition details
    with st.expander("Enter Petition Details"):
        petitioner = st.text_input("Petitioner Name")
        respondent = st.text_input("Respondent Name")
        facts      = st.text_area("Facts of the Case")
        relief     = st.text_area("Relief Sought")
        if st.button("Generate Petition"):
            # Build prompt for the model
            prompt = f"""Draft a legal petition under Pakistani family law with the following details:
Petitioner: {petitioner}
Respondent: {respondent}
Facts: {facts}
Relief Sought: {relief}
"""
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


