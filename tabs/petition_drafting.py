#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:14:28 2025
@author: amna
"""

import os
import streamlit as st
from groq import Groq

# Set up Groq client using environment variable or Streamlit secret
api_key = st.secrets.get("GROQ_KEY") or os.getenv("GROQ_KEY")

class GroqLLM:
    def __init__(self, model="llama3-70b-8192", api_key=None):
        self.client = Groq(api_key=api_key)
        self.model = model

    def complete(self, prompt):
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.7
        )
        return type('obj', (object,), {'text': response.choices[0].message.content})

llm = GroqLLM(model="llama3-70b-8192", api_key=api_key)

SYSTEM_PROMPT = """You are a seasoned Pakistani family law practitioner. Draft clear, concise legal petitions based on user-provided case details, following Pakistani court conventions."""

def render(client):
    tab_name = "Petition Drafting"

    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    st.header("Petition Drafting || درخواست کا مسودہ")

    with st.expander("📄 Fill Petition Form"):
        user_inputs = {}
        questions = [
            ("wife_name", "1. Full name of the wife (plaintiff):"),
            ("wife_father", "2. What is the father’s name of the wife?"),
            ("wife_cnic", "3. What is the CNIC number of the wife?"),
            ("wife_address", "4. Current address of the wife:"),
            ("husband_name", "5. Full name of the husband (defendant):"),
            ("husband_father", "6. Father’s name of the husband:"),
            ("husband_address", "7. Address of the husband:"),
            ("marriage_date_city", "8. City and date of marriage:"),
            ("haq_mehr", "9. Haq Mehr amount and whether paid:"),
            ("children", "10. Any children? Provide names and dates of birth:"),
            ("separation_duration", "11. Duration of separation:"),
            ("maintenance", "12. Has husband paid any maintenance?"),
            ("khula_reasons", "13. Reasons for seeking Khula:"),
            ("divorce_requests", "14. Have you requested divorce? What was his response?"),
            ("cause_recent", "15. When did the cause of action arise?"),
            ("filing_city", "16. City where this suit will be filed:"),
            ("lawyer_name", "17. Do you want to include lawyer's name? If yes, enter full name."),
        ]

        for key, question in questions:
            user_inputs[key] = st.text_input(question)

        if st.button("📜 Generate Petition"):
            formatted = "\n".join([f"{key}: {val}" for key, val in user_inputs.items() if val.strip() != ""])
            petition_prompt = f"""Using the following information given as input, draft a formal Khula Petition in English for submission in Pakistani Family Court.

{formatted}

Start now:"""

            
            

            # Send prompt silently (don't display user input)
            st.session_state.messages[tab_name].append({"role": "user", "content": petition_prompt})
            
            # Only show assistant response
            with st.chat_message("assistant"):
                output = llm.complete(petition_prompt).text
                st.markdown(output)
                st.download_button(
                    label="💾 Download Petition as .txt",
                    data=output,
                    file_name="khula_petition.txt",
                    mime="text/plain"
                )
            
            st.session_state.messages[tab_name].append({"role": "assistant", "content": output})
