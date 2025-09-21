#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Role Integration Module – Ferrosa App

WhatsApp-style training to help Pakistani women entrepreneurs
learn how to balance multiple family and work responsibilities.

"""

import streamlit as st
import json


# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are Zara — a warm, supportive mentor who helps low-income Pakistani women 
(with limited education and digital exposure) learn how to balance their family 
and work responsibilities with confidence. You guide them through WhatsApp-style 
sessions using relatable examples, small practical tips, and encouragement.

In THIS MODULE WE TEACH THIS:
- Recognizing and balancing multiple roles (mother, wife, daughter-in-law, businesswoman, etc.).
- Identifying strengths and qualities that help in these roles.
- Simple daily strategies to manage conflicts between family and work.
- Building confidence in handling responsibilities step by step.

Your response rules:
- Always in English, WhatsApp-style (short, 2–5 lines).
- Use simple, relatable examples from daily family and work life.
- No jargon. No long paragraphs.
- Be empathetic and encouraging.
- If off-topic, kindly redirect back to role balance.
"""


# -----------------------------
# Pre-scripted conversation messages
# -----------------------------
msg_357 = (
    "Welcome back! 👋\n\n"
    "Today, we’ll talk about **balancing different roles** — like being a mother, wife, daughter-in-law, and businesswoman.\n\n"
    "Every woman wears many hats. Let’s see how you balance yours. Ready?"
)

msg_358 = (
    "Think about yourself. Which roles do you usually play in your daily life?\n\n"
    "1️⃣ Mother\n2️⃣ Wife\n3️⃣ Daughter-in-law\n4️⃣ Businesswoman\n5️⃣ Other"
)

msg_358A = "Great! Now, name **3–5 personal qualities** that help you manage these roles (e.g., patience, planning, energy)."


msg_360 = (
    "Well done 🙌 You’ve completed the step-by-step part of this module.\n\n"
    "If you have any questions about role balance or family/work tips, feel free to ask me now."
)


# -----------------------------
# Session Setup
# -----------------------------
def setup_session_state(tab_name: str):
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    if "ri_stage" not in st.session_state:
        st.session_state.ri_stage = 0
    if "ri_roles" not in st.session_state:
        st.session_state.ri_roles = ""
    if "ri_qualities" not in st.session_state:
        st.session_state.ri_qualities = ""
    if "ri_challenge" not in st.session_state:
        st.session_state.ri_challenge = ""


# -----------------------------
# Show chat history
# -----------------------------
def display_chat_history(tab_name: str):
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


# -----------------------------
# MAIN RENDER FUNCTION
# -----------------------------
def render(client):
    tab_name = "Identifying the right person"
    st.header("Role Integration: Balancing Family and Work")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # INTRO → 358
    if st.session_state.ri_stage == 0:
        if not any(msg["content"] == msg_357 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_357})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_358})

        choice = st.multiselect(
            "Select your roles:",
            ["Mother", "Wife", "Daughter-in-law", "Businesswoman", "Other"],
            key="ri_stage0_multi",
        )
        if choice:
            st.session_state.ri_roles = ", ".join(choice)
            st.session_state.messages[tab_name].append({"role": "user", "content": st.session_state.ri_roles})
            st.session_state.ri_stage = 1
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_358A})

    # 358A → qualities
    elif st.session_state.ri_stage == 1:
        qualities = st.text_input("Type 3–5 qualities:", key="ri_stage1_input")
        st.session_state.ri_qualities = qualities
        if qualities:
            st.session_state.ri_qualities = qualities
            st.session_state.messages[tab_name].append({"role": "user", "content": qualities})
            st.session_state.ri_stage = 3
    
            # Build LLM JSON feedback
            system_prompt_demo = f"""
You are Zara — a warm, supportive mentor who helps low-income Pakistani women 
(with limited education and digital exposure) learn how to balance their family 
and work responsibilities with confidence. You guide them through WhatsApp-style 
sessions using relatable examples, small practical tips, and encouragement.Dont be very casual no need to greet here.

INPUT:
- Roles: {st.session_state.ri_roles}
- Qualities: {st.session_state.ri_qualities}

Your task:  
1. If user gives 3–5 clear qualities/skills, celebrate warmly.  
   - Reinforce each quality with reasoning or an example.  
     For example: If they say “trustworthy,” you might add, “Yes, because you can rely on them with money or children without worry.”  
   - Encourage reflection *inside the feedback itself* without asking them to type again. (e.g., “These qualities show you thought carefully about this person — it’s clear why they’re a strong choice.”)  

2. If user gives fewer than 3, or vague/negative responses (e.g., “just available”), guide gently.  
   - Appreciate what they shared.  
   - Suggest simple, concrete qualities they could add (e.g., reliable, caring, experienced).  
   - Reinforce by explaining why those qualities matter in daily life.  

3. If user gives unrelated responses, redirect with kindness.  
    - Acknowledge their input try to make sense of their input
   - Explain what “qualities or skills” mean with an example.  
   - Encourage them to think of 3–5 qualities of the person.  

NOTE: Always respond in English, WhatsApp-style (short, 2–5 lines). Use simple, relatable examples from daily family and work life. No jargon. No long paragraphs. Be empathetic and encouraging.

Output ONLY JSON:
{{"feedback": "<empathetic WhatsApp-style response>", "is_correct": true/false}}
"""
            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": "system", "content": system_prompt_demo}],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thank you for sharing.")
            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)

            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_360})
            st.session_state.ri_stage = 4
            st.rerun()

    # Freeform chat after 360
    elif st.session_state.ri_stage >= 4:
        if prompt := st.chat_input("Chat with Zara (Role Integration)"):
            st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages[tab_name]

            with st.chat_message("assistant"):
                try:
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=llm_messages,
                        stream=True,
                    )
                    response = st.write_stream(stream)
                except Exception as e:
                    response = f"⚠️ Error: {e}"
                    st.error(response)

            st.session_state.messages[tab_name].append({"role": "assistant", "content": response})
