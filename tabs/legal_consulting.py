#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
"""
Psychological development of Female entrepreneurs for Ferrosa App

Chat interface for Pakistani women entrepreneurs to learn how to express themselves
using I- and We-statements in personal/business life.

Adapted on Wed July 10 2025
@author: amna
"""

import streamlit as st
import time
import json


# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------
DEFAULT_MODEL = "ft:gpt-4o-2024-08-06:iml-research:wakeel:BW4oryHJ"

SYSTEM_PROMPT = """
You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) understand how to build small businesses with the support of their families. You guide them through a WhatsApp-style training focused on communication skills and family support — not technical business skills (yet).

Specifically in this module you are helping the user learn how to express themselves better using I-Statements and We-Statements.

1. Separating people from the problem – using "I" and "We" statements to reduce blame  

Your response rules:
- Always respond in english and if you cant decipher the language, just redirect to the topic adter saying i dont undertstand what you said
- Always include one example of a correct I- or We-Statement that is relatable to a Pakistani woman entrepreneur’s life.
- Keep replies short (under 5 lines per language), like WhatsApp messages  
- If user asks about Role Integration, Stress, Branding, or Digital Skills, politely say that will come in future sessions and redirect to this topic.
- If question is unrelated (e.g. health, religion, legal issues), kindly redirect to this topic.
- Be empathetic, simple, and avoid complex words.

Now kindly answer the user’s question with warmth and clarity.
"""

# -----------------------------
# Pre-scripted conversation messages
# -----------------------------
msg1 = (
    "Welcome back, it's nice to see you again! 👋\n\n"
    "Last time, we talked about trying out I- and WE Statements in real life.\n"
    "**Did you get a chance to try I statements?**\n\n"
    "1 - Yes, I did!\n"
    "2 - Not yet"
)

msg2_yes = "Wonderful! Write your I statement that you used in real life. I’ll look at it with you."

msg2_no = (
    "No worries! Let’s try one together now.\n\n"
    "**Example**:\n_I feel left out when business decisions are made without me._\n\n"
    "Now it’s your turn. Try writing an I statement from your life."
)

msg3_we_intro = (
    "Last time, we ALSO talked about trying out We-Statements in real life.\n"
    "**Did you get a chance to try one?**\n\n"
    "1 - Yes, I did!\n"
    "2 - Not yet"
)

msg4_we_example = (
    "No worries! Let’s try one together now.\n\n"
    "**Example**: _We feel more confident when we help each other at the market._\n\n"
    "Your turn—write a We-statement from your own life."
)

msg3_reflection = (
    "It makes a huge difference when you take a moment to think about how to say something in a better way. 💬\n"
    "Now you know how to take the first step: separate yourself from the issue and speak without damaging relationships. ❤️"
)

# -----------------------------
# Session Setup
# -----------------------------
def setup_session_state(tab_name: str):
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = DEFAULT_MODEL
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    if "iwe_stage" not in st.session_state:
        st.session_state.iwe_stage = 0
    if "iwe_i_statement" not in st.session_state:
        st.session_state.iwe_i_statement = ""
    if "iwe_we_statement" not in st.session_state:
        st.session_state.iwe_we_statement = ""

# -----------------------------
# Show chat history (only from stage 2+)
# -----------------------------
def display_chat_history(tab_name: str):
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -----------------------------
# Freeform LLM chat (after rule-based part is done)
# -----------------------------
def handle_user_prompt(client, tab_name: str):
    if prompt := st.chat_input("Chat with Zara (I WE Statements)"):
        st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages[tab_name],
                    stream=True,
                )
                response = st.write_stream(stream)
            except Exception as e:
                response = f"⚠️ Error: {e}"
                st.error(response)
        st.session_state.messages[tab_name].append({"role": "assistant", "content": response})

# -----------------------------
# MAIN RENDER FUNCTION
# -----------------------------
def render(client):
    tab_name = "I WE Statements"
    st.header("I- and We-Statements Training")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # STAGE 0: Ask if they tried I/We statement
    if st.session_state.iwe_stage == 0:
        if not any(msg["content"] == msg1 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1})
            display_chat_history(tab_name)

        user_response = st.chat_input("Type 1 or 2")
        if user_response:
            st.session_state.messages[tab_name].append({"role": "user", "content": user_response})
            if user_response.strip() == "1":
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2_yes})
            else:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2_no})
            st.session_state.iwe_stage = 1
            display_chat_history(tab_name)

    # STAGE 1: Collect I-statement
    elif st.session_state.iwe_stage == 1:
        iwe_input = st.chat_input("Write your I-statement")
        if iwe_input:
            st.session_state.iwe_i_statement = iwe_input
            st.session_state.messages[tab_name].append({"role": "user", "content": iwe_input})

            # Prompt that asks for feedback AND a validity flag
            system_prompt = """
    You are a communication coach helping users write clear I-statements.

    Your task is to:
    1. Give short feedback on the user’s I-statement. BUT BE KIND AND SUPPORTIVE.
    2. Provide an example of a good I-statement that is relatable to a Pakistani low socio economic women entrepreneur.
    3. Not point out their grammatical or spelling mistakes, but focus on the clarity and structure of the I-statement.
    4. Dont say directly whether it is a valid I-statement or not (True/False) ;sugar coat it .

    Respond ONLY in JSON format like this:
    {"feedback": "Your I-statement is clear and well-structured!", "is_valid": true}
            """

            try:
                # Get streamed response
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"My I-statement: {iwe_input}"}
                    ],
                    stream=False,  # not streaming so we can parse JSON
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thanks for your response.")
                is_valid = result.get("is_valid", False)

            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)
                feedback = "Sorry, something went wrong."
                is_valid = False

            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})

            if is_valid:
                # Move to next stage
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_we_intro})
                st.session_state.iwe_stage = 2

            else:
                if not st.session_state.get("iwe_retry", False):
                    # First invalid attempt → give another try
                    st.session_state.iwe_retry = True
                    st.session_state.messages[tab_name].append({
                        "role": "assistant",
                        "content": "Try again to write an I statement"
                        ""
                    })
                else:
                    # Second invalid attempt → move on anyway
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_we_intro})
                    st.session_state.iwe_stage = 2

            display_chat_history(tab_name)



    # STAGE 2: Ask if they tried a We-statement
    elif st.session_state.iwe_stage == 2:
        user_response = st.chat_input("Type 1 or 2")
        if user_response:
            st.session_state.messages[tab_name].append({"role": "user", "content": user_response})
            if user_response.strip() == "1":
                st.session_state.messages[tab_name].append({"role": "assistant", "content": "Great! Write your We-statement and I will check it."})
            else:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4_we_example})
            st.session_state.iwe_stage = 3
            display_chat_history(tab_name)

    # STAGE 3: Collect We-statement
    elif st.session_state.iwe_stage == 3:
        we_input = st.chat_input("Write your We-statement")
        if we_input:
            st.session_state.iwe_we_statement = we_input
            st.session_state.messages[tab_name].append({"role": "user", "content": we_input})
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"My We-statement: {we_input}"}
                    ],
                    stream=True,
                )
                feedback = st.write_stream(stream)
            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)
                feedback = "Sorry, something went wrong."
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})

            # Send both I and We for overall reflection
            try:
                reflection_prompt = f"The user shared this I-statement: {st.session_state.iwe_i_statement} and this We-statement: {st.session_state.iwe_we_statement}. Give them final encouragement and reflection."
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": reflection_prompt}
                    ],
                    stream=True,
                )
                final_feedback = st.write_stream(stream)
            except Exception as e:
                final_feedback = f"⚠️ Error from LLM: {e}"
                st.error(final_feedback)
                final_feedback = "Thanks for trying this out!"

            st.session_state.messages[tab_name].append({"role": "assistant", "content": final_feedback})
            st.session_state.iwe_stage = 4
            display_chat_history(tab_name)

    # STAGE 4+: Open-ended chat
    elif st.session_state.iwe_stage >= 4:
        handle_user_prompt(client, tab_name)


