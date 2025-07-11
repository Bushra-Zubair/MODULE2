#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Zara Streamlit app.
Customized by Bushra for Zara Entrepreneur chatbot.
"""

import os
import streamlit as st
from openai import OpenAI

# Keep original tab modules (so no import error)
from tabs import legal_consulting, petition_drafting, citations_retrieval

def main():
    st.set_page_config(page_title="Zara | زارا", layout="centered")
    st.title("Zara || زارا - Family Support Assistant")

    # OpenAI API initialization
    try:
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found.")
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        return

    # Keep Groq key handling as before
    try:
        groq_key = st.secrets.get("GROQ_KEY")
        if not groq_key:
            raise ValueError("Groq API key not found.")
        os.environ["GROQ_API_KEY"] = groq_key
    except Exception as e:
        st.error(f"Failed to set Groq API key: {e}")
        return

    # Session state
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "o4-mini-2025-04-16"
    if "messages" not in st.session_state:
        st.session_state["messages"] = {}

    # Sidebar options mapped to original tab modules, but with your new labels
    label_map = {
        "Understanding Your Partner’s Interests/Communication Help ": petition_drafting,
        "‘I We’ Statements ": legal_consulting,
        "General Flow ": citations_retrieval
    }

    choice = st.radio("Which topic do you want to try first?", list(label_map.keys()))

    module = label_map[choice]
    module.render(client)

if __name__ == "__main__":
    main()
