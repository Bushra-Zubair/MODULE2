#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Petition Drafting Tab for Streamlit App "Wakeel"
Drafts Khula petitions using a language model based on user-provided inputs.
Created on Wed May 14 15:14:28 2025
@author: amna
"""

import os
import streamlit as st
from groq import Groq

# System prompt for consistent behavior of LLM
SYSTEM_PROMPT = """You are a seasoned Pakistani family law practitioner. Draft clear, concise legal petitions based on user-provided case details, following Pakistani court conventions."""

# Initialize Groq API key from Streamlit secrets or environment
api_key = st.secrets.get("GROQ_KEY") or os.getenv("GROQ_KEY")


class GroqLLM:
    """
    Wrapper class for interacting with the Groq chat completion model.
    """

    def __init__(self, model="llama3-70b-8192", api_key=None):
        self.client = Groq(api_key=api_key)
        self.model = model

    def complete(self, prompt: str):
        """
        Get completion from Groq model for a given prompt.
        Returns a mock object with a 'text' attribute for compatibility.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return type('obj', (object,), {'text': response.choices[0].message.content})


# Instantiate LLM
llm = GroqLLM(api_key=api_key)


def render(client):
    """
    Main rendering function for Petition Drafting tab.
    Allows selection of petition type and generates legal petition using Groq LLM.
    """
    tab_name = "Petition Drafting"

    # Initialize chat history for this tab
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = []

    # Select petition type
    st.header("Petition Drafting || درخواست کا مسودہ")
    petition_type = st.selectbox(
        "📌 Select type of petition to draft:",
        options=["Khula", "Child Custody", "Maintenance"]
    )

    # Define contextual system prompt based on selected type
    prompt_map = {
        "Khula": "You are a seasoned Pakistani family law practitioner. Draft a clear, concise Khula petition based on user-provided case details, following Pakistani court conventions.",
        "Child Custody": "You are a seasoned Pakistani family law practitioner. Draft a clear, persuasive child custody petition based on user-provided details, following legal norms and child welfare principles.",
        "Maintenance": "You are a seasoned Pakistani family law practitioner. Draft a formal petition for spousal or child maintenance based on user inputs, per Pakistani family law."
    }
    system_prompt = prompt_map[petition_type]

    # Save system prompt in message history
    if not any(m["role"] == "system" for m in st.session_state.messages[tab_name]):
        st.session_state.messages[tab_name].append({"role": "system", "content": system_prompt})

    with st.expander(f"📝 Fill Petition Form ({petition_type})"):
        user_inputs = {}
        common_questions = [
            ("wife_name", "1. Full name of the wife (plaintiff):"),
            ("wife_father", "2. What is the father’s name of the wife?"),
            ("wife_cnic", "3. What is the CNIC number of the wife?"),
            ("wife_address", "4. Current address of the wife:"),
            ("husband_name", "5. Full name of the husband (defendant):"),
            ("husband_father", "6. Father’s name of the husband:"),
            ("husband_address", "7. Address of the husband:"),
        ]

        khula_specific = [
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

        custody_specific = [
            ("children_details", "8. Names and birth dates of children:"),
            ("custody_reason", "9. Why are you seeking custody?"),
            ("husband_custody_response", "10. What is the husband’s stance on custody?"),
            ("financial_means", "11. Can you financially support the child(ren)?"),
            ("school_info", "12. Where do children currently study/live?"),
            ("filing_city", "13. City where this suit will be filed:"),
            ("lawyer_name", "14. Lawyer’s name (if any):"),
        ]

        maintenance_specific = [
            ("maintenance_reason", "8. Who needs maintenance and why?"),
            ("income_details", "9. Do you or your spouse have a source of income?"),
            ("previous_support", "10. Has the husband provided any financial support before?"),
            ("children_details", "11. Child(ren) name(s) and expense needs:"),
            ("filing_city", "12. City where this suit will be filed:"),
            ("lawyer_name", "13. Lawyer’s name (if any):"),
        ]

        type_specific = {
            "Khula": khula_specific,
            "Child Custody": custody_specific,
            "Maintenance": maintenance_specific
        }

        # Generate form fields dynamically
        for key, label in common_questions + type_specific[petition_type]:
            user_inputs[key] = st.text_input(label)

        # Submit button
        if st.button("📜 Generate Petition"):
            # Format prompt
            formatted = "\n".join([f"{k}: {v}" for k, v in user_inputs.items() if v.strip()])
            petition_prompt = (
                f"Using the following information, draft a formal {petition_type} Petition in English for submission in Pakistani Family Court:\n\n"
                f"{formatted}\n\nStart now:"
            )

            st.session_state.messages[tab_name].append({"role": "user", "content": petition_prompt})

            with st.chat_message("assistant"):
                output = llm.complete(petition_prompt).text
                st.markdown(output)
                st.download_button(
                    label="💾 Download Petition as .txt",
                    data=output,
                    file_name=f"{petition_type.lower().replace(' ', '_')}_petition.txt",
                    mime="text/plain"
                )

            st.session_state.messages[tab_name].append({"role": "assistant", "content": output})
