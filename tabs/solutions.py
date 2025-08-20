
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import time
import json

# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) better understand and manage stress and build self-confidence in their entrepreneurial journey. You guide them through WhatsApp-style sessions using relatable examples, emotional validation, and simple tools like breathing exercises and daily reflection.

In THIS MODULE WE TEACH THIS:
- What stress is, where it comes from, and how to manage it using the Transactional Model of Stress & Coping.
- Identifying stressors and seeing them from a different, more positive perspective.
- Breathing and mindfulness exercises to reduce anxiety and build clarity.
- Simple reflections and diary work to build self-confidence and self-awareness.
- That self-confidence grows from your strengths, supportive relationships, and belief in yourself.

Your response rules:
- Always respond in English; if user types in another language and it's unclear, say "I didn't understand that. Let's return to today's topic" and gently redirect.
- Always include one simple, relatable example from the life of a Pakistani woman (e.g. family pressure, business delays, children, or health worries).
- Keep replies short (max 5 lines), like WhatsApp messages.
- If the user asks about Role Integration, Branding, or Money Management, kindly say, "That will come in future sessions 😊" and return to the topic.
- If the user asks about unrelated topics (e.g. marriage, politics, religion), gently bring focus back with kindness.
- Be warm, empathetic, supportive — like an older sister helping you breathe and believe again.

Now kindly answer the user's question with warmth and clarity.
"""

# -----------------------------
# Pre-scripted conversation messages
# -----------------------------
msg1 = """Let's start by practicing this with an example. Meet Nazia. She runs a business and feels very stressed right now.

Nazia: "I have some bad news: The landlord of my store wants to raise the rent!"\n
Husband: "Seriously? How much more does he want?"\n
Nazia: "Too much! I can't afford that! It threatens my entire business. If I have to pay more, there will hardly be anything left for us. I don't know what to do!"\n

This is a stressful situation for Nazia. Can you help her by thinking of solutions?"""

msg2 = """Please write down solutions for Nazia's situation and send them here in the chat so we can look at them together."""

msg3_partner_intro = """I have also thought of one possible solution: Nazia can stop renting her shop and shift her business entirely online. This will save money and help her use the money for other things in her business.\n
Now You think about how this solution can help Nazia manage her stress better and write that down here in the chat."""

msg4_reflection = """Great work! You see, when we face stressful situations like Nazia's rent problem, the key is to:
1. Stay calm and think of solutions
2. Look for different options instead of panicking
3. Remember that every problem has a solution

This helps us manage stress better and build confidence in ourselves. When you practice this, you'll feel stronger in difficult situations too!"""

# -----------------------------
# Session Setup
# -----------------------------
def setup_session_state(tab_name: str):
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    if "stress_stage" not in st.session_state:
        st.session_state.stress_stage = 0
    if "user_solution" not in st.session_state:
        st.session_state.user_solution = ""
    if "user_retry" not in st.session_state:
        st.session_state.user_retry = False

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
    if prompt := st.chat_input("Chat with Zara (Stress Management)"):
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
    tab_name = "Stress Management"
    st.header("Managing Stress Through Problem-Solving")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # STAGE 0: Present Nazia's stressful situation
    if st.session_state.stress_stage == 0:
        if not any(msg["content"] == msg1 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2})
            display_chat_history(tab_name)
        
        st.session_state.stress_stage = 1

    # STAGE 1: Collect user's solution for Nazia
    elif st.session_state.stress_stage == 1:
        user_input = st.chat_input("What solutions can you think of for Nazia?")
        if user_input:
            st.session_state.user_solution = user_input
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})

            # Evaluate the user's solution
            system_prompt = """
            You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) better understand and manage stress and build self-confidence in their entrepreneurial journey. You guide them through WhatsApp-style sessions. HERE You are evaluating if a user has provided a helpful solution to a business stress situation.

            The situation: Nazia's landlord wants to raise rent for her store, threatening her business.

            Your task:
            1. If the user provides a reasonable, actionable solution (e.g., "move online", "negotiate with landlord", 
            "find a cheaper location", "increase prices", "cut expenses", "share shop space"), consider it correct. 
            - Appreciate the effort warmly.
            - Briefly explain **why the solution works** in Nazia’s case (e.g., lowers expenses, reduces pressure, 
                helps her stay in control).

            2. If the user provides a partial solution or shows understanding but lacks detail, consider it partially correct. 
            - Encourage the effort kindly.
            - Suggest adding more specific, actionable steps.

            3. If the user gives an unrelated response, only an emotional reaction, or no real solution, consider it incorrect. 
            - Thank them gently for sharing.
            - Encourage them to think of **practical steps** Nazia could take about her rent problem.
            - Give one or two short examples of practical solutions (e.g., negotiate with landlord, look for a cheaper shop) 
                and invite them to try again.

            -Evaluate the solution and provide encouraging feedback in simple english;Be warm, empathetic, supportive — like an older sister helping you breathe and believe again.

            Respond ONLY in JSON format like this:
            {"feedback": "That's a great solution! Moving online would definitely help save money because it lowers expenses and gives Nazia more control.", "is_correct": true}
            """
            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"User's solution: {user_input}"}
                    ],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thank you for thinking about this.")
                is_correct = result.get("is_correct", False)

            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)
                feedback = "Thank you for thinking about this."
                is_correct = False

            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})

            if is_correct:
                # If correct, appreciate and elaborate
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_partner_intro})
                st.session_state.stress_stage = 2
            elif not st.session_state.user_retry:
                # Give one retry
                st.session_state.user_retry = True
                st.session_state.messages[tab_name].append({
                    "role": "assistant", 
                    "content": "Think about what specific actions Nazia could take to solve her rent problem. What are some practical steps she could try?"
                })
            else:
                # After retry, provide correct answer
                st.session_state.messages[tab_name].append({
                    "role": "assistant", 
                    "content": "Let me share a solution with you: " + msg3_partner_intro
                })
                st.session_state.stress_stage = 2

            display_chat_history(tab_name)

    # STAGE 2: Provide reflection on stress management
    elif st.session_state.stress_stage == 2:
        if not any(msg["content"] == msg4_reflection for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4_reflection})
            st.session_state.stress_stage = 3
            display_chat_history(tab_name)

    # STAGE 3+: Open-ended chat about stress management
    elif st.session_state.stress_stage >= 3:
        handle_user_prompt(client, tab_name)