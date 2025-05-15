#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:10:15 2025

@author: amna
"""

import os
import streamlit as st
from openai import OpenAI

from tabs import legal_consulting, petition_drafting, citations_retrieval

def main():
    
    # 1. Page config
    st.set_page_config(page_title="Wakeel | وکیل", layout="centered")
    st.title("Wakeel || وکیل")
    

    # 2. OpenAI client (read key from secrets/env)
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    client  = OpenAI(api_key=api_key)
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_KEY"]


    # 3. Session defaults
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "o4-mini-2025-04-16"
    if "messages" not in st.session_state:
        st.session_state["messages"] = {}

    # 4. Tab selection
    label_map = {
        "Legal Consulting || قانونی رہنمائی":   legal_consulting,
        "Petition Drafting || درخواست کا مسودہ": petition_drafting,
        "Citations Retrieval || قانونی حوالہ جات": citations_retrieval
    }
    choice = st.radio("آپ کو کس قانونی معاملے میں مدد چاہیے؟", list(label_map.keys()))

    # 5. Call the chosen tab’s `render` function
    module = label_map[choice]
    module.render(client)

if __name__ == "__main__":
    main()
