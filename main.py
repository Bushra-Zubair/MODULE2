#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Wakeel Streamlit app.
Handles UI layout, API initialization, and tab routing.
Created on Wed May 14 15:10:15 2025
@author: amna
"""

import os
import streamlit as st
from openai import OpenAI

# Import tab modules
from tabs import legal_consulting, petition_drafting, citations_retrieval

def main():
    # 1. Configure page layout and title
    st.set_page_config(page_title="Wakeel | وکیل", layout="centered")
    st.title("Wakeel || وکیل")

    # 2. Load API keys from secrets or environment variables with error handling
    try:
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in Streamlit secrets or environment variables.")
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        return

    try:
        groq_key = st.secrets.get("GROQ_KEY")
        if not groq_key:
            raise ValueError("Groq API key not found in Streamlit secrets.")
        os.environ["GROQ_API_KEY"] = groq_key
    except Exception as e:
        st.error(f"Failed to set Groq API key: {e}")
        return

    # 3. Initialize session state for model selection and message history
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "o4-mini-2025-04-16"
    if "messages" not in st.session_state:
        st.session_state["messages"] = {}

    # 4. Sidebar or main section radio button for selecting legal help type
    label_map = {
        "Legal Consulting || قانونی رہنمائی":   legal_consulting,
        "Petition Drafting || درخواست کا مسودہ": petition_drafting,
        "Citations Retrieval || قانونی حوالہ جات": citations_retrieval
    }

    # Display tab selection prompt to user in Urdu
    choice = st.radio("آپ کو کس قانونی معاملے میں مدد چاہیے؟", list(label_map.keys()))

    # 5. Load and run the appropriate module's render() method
    module = label_map[choice]
    module.render(client)

# Run main only when this script is executed directly
if __name__ == "__main__":
    main()
