
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Understanding Your Partner's Interests for Female Entrepreneurs – Ferrosa App

WhatsApp-style training to help Pakistani women entrepreneurs understand
both sides' perspectives and create win-win solutions.

Adapted on Thu July 11 2025
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
You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) understand how to build small businesses with the support of their families. You guide them through a WhatsApp-style training focused on understanding different perspectives and creating win-win solutions.

In THIS MODULE WE TEACH THIS:
- Understanding both sides' true needs helps create solutions where everyone benefits.
- Think about the other person's perspective and interests.
- Remember: It's you + them vs. the problem.

Your response rules:
- Always respond in english and if you cant decipher the language, just redirect to the topic after saying i dont understand what you said
- Always include one example of understanding someone else's perspective that is relatable to a Pakistani woman entrepreneur's life.
- Keep replies short (under 5 lines per language), like WhatsApp messages
- If user asks about Role Integration, Stress, Branding, or Digital Skills, politely say that will come in future sessions and redirect to this topic.
- If question is unrelated (e.g. health, religion, legal issues), kindly redirect to this topic.
- Be empathetic, simple, and avoid complex words.

Now kindly answer the user's question with warmth and clarity.
"""

# -----------------------------
# Pre-scripted conversation messages
# -----------------------------
msg1 = (
    "Welcome back! 👋\n\n"
    "Today we're going to practice understanding what matters to both sides in a disagreement.\n"
    "**Can you remember a time when you had to sort something out with a family member?**\n"
    "Maybe with your partner, children, or any other family member?\n\n"
    "1 - Yes, I remember something!\n"
    "2 - Not really"
)

msg2_yes = (
    "Amazing! What was important to YOU in that situation?\n"
    "Please write it right here in the chat so we can look at it together."
)

msg2_no = (
    "That's okay! Let's try one together now.\n\n"
    "**Example**: Imagine your husband was upset about money being spent without asking him.\n"
    "Maybe your interest was buying something useful for the family, and his interest was staying in control of the budget.\n\n"
    "Now can you think of a moment like that? What was important to YOU in that situation?"
)

msg3_partner_intro = (
    "Now let's think about the other person.\n"
    "**What do you think their interest was in that situation?**\n\n"
    "1 - I think I know!\n"
    "2 - I'm not sure"
)

msg4_partner_example = (
    "You're not sure what their interest is? That's okay!\n\n"
    "Try to see things from their perspective — why might they feel that way or act like they did?\n\n"
    "**Example**: If someone gets upset about spending, maybe they're worried about having enough money for emergencies.\n\n"
    "Now try again — what do you think was important to them?"
)

msg3_reflection = (
    "Understanding both sides is the key to finding solutions that work for everyone! 🤝\n"
    "When you see it's not you vs. them, but both of you vs. the problem, everything changes. 💡"
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
    if "partner_stage" not in st.session_state:
        st.session_state.partner_stage = 0
    if "user_interest" not in st.session_state:
        st.session_state.user_interest = ""
    if "partner_interest" not in st.session_state:
        st.session_state.partner_interest = ""

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
    if prompt := st.chat_input("Chat with Zara (Understanding Partners)"):
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
    tab_name = "Understanding Partners"
    st.header("Understanding Your Partner's Interests")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # STAGE 0: Ask if they remember a family disagreement
    if st.session_state.partner_stage == 0:
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
            st.session_state.partner_stage = 1
            display_chat_history(tab_name)

    # STAGE 1: Collect user's interest
    elif st.session_state.partner_stage == 1:
        user_input = st.chat_input("What was important to you?")
        if user_input:
            st.session_state.user_interest = user_input
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})

            # Prompt that asks for feedback on user's interest
            system_prompt = """
You are a communication coach helping users understand their own interests in conflicts.

Your task is to:
1. Give short, supportive feedback on what the user shared about their interest.
2. Provide an example of a similar interest that Pakistani women entrepreneurs might have.
3. Be kind and encouraging - don't critique, just acknowledge their perspective.
4. Assess if their response shows they understand what an "interest" means (their underlying need/concern).


Your task:
1. If the user has written a clear and relevant interest/need (e.g., "I needed time to work on my orders without being disturbed"), give supportive and positive feedback.
2. If the user has made a sincere attempt but their response is vague or only describes emotions (e.g., “I felt sad”), gently guide them to connect that emotion to a real **need or interest**.
3. If the message is off-topic or doesn’t relate to a situation of family support, kindly redirect and give an example to bring them back on track.
Respond ONLY in JSON format like this:
{"feedback": "I understand that was important to you!", "is_valid": true}
            """

            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"My interest was: {user_input}"}
                    ],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thanks for sharing that.")
                is_valid = result.get("is_valid", False)

            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)
                feedback = "Thanks for sharing that with me."
                is_valid = False

            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})

            if is_valid:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_partner_intro})
                st.session_state.partner_stage = 2
            else:
                if not st.session_state.get("user_retry", False):
                    st.session_state.user_retry = True
                    st.session_state.messages[tab_name].append({
                        "role": "assistant",
                        "content": "Can you tell me more about what was really important to you in that situation?"
                    })
                else:
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_partner_intro})
                    st.session_state.partner_stage = 2

            display_chat_history(tab_name)

    # STAGE 2: Ask if they can identify partner's interest
    elif st.session_state.partner_stage == 2:
        user_response = st.chat_input("Type 1 or 2")
        if user_response:
            st.session_state.messages[tab_name].append({"role": "user", "content": user_response})
            if user_response.strip() == "1":
                st.session_state.messages[tab_name].append({"role": "assistant", "content": "Great! Please write what you think was important to them."})
            else:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4_partner_example})
            st.session_state.partner_stage = 3
            display_chat_history(tab_name)

    # STAGE 3: Collect partner's interest
    elif st.session_state.partner_stage == 3:
        partner_input = st.chat_input("What do you think was important to them?")
        if partner_input:
            st.session_state.partner_interest = partner_input
            st.session_state.messages[tab_name].append({"role": "user", "content": partner_input})

            # Get LLM feedback on partner interest understanding
            system_prompt = """
You are a communication coach helping users understand other people's interests in conflicts.

Your task is to:
1. Give short, supportive feedback on the user's attempt to understand the other person's interest.
2. Provide gentle guidance if they're off track, with examples.
3. Be encouraging and focus on the effort they made to see the other perspective.
4. Assess if their response shows empathy and understanding of the other person's underlying needs.


Your task:
1. If the user makes a reasonable guess about the family member’s interest (e.g., “She wanted me to help with the kids because she was overwhelmed”), give warm, supportive feedback like “Great! This helps you clearly see what the main concern in the situation is.”
2. If the user shares only emotions or judgments about the other person (e.g., “She was being unfair” or “They were just controlling”), gently redirect and encourage empathy by giving a better example.
3. If the user input is unrelated or too vague, say so kindly and guide them back with a simple, relatable example.

Respond ONLY in JSON format like this:
{"feedback": "That shows you're really trying to understand their perspective!", "is_valid": true}
            """

            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"I think their interest was: {partner_input}"}
                    ],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thanks for thinking about their perspective.")
                is_valid = result.get("is_valid", False)

            except Exception as e:
                feedback = f"⚠️ Error from LLM: {e}"
                st.error(feedback)
                feedback = "Thanks for thinking about their perspective."
                is_valid = False

            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})

            if is_valid:
                # Generate final reflection using both interests
                try:
                    reflection_prompt = f"""
The user shared:
- Their interest: {st.session_state.user_interest}
- Partner's interest: {st.session_state.partner_interest}

Give them a final reflection that:
1. Acknowledges both perspectives
2. Shows how understanding both sides helps find solutions DONT LET THEM BE LITTLE THE OTHER PERSON PEREPSCTIVE ; MAKE THEM FEEL LIKE THEY ARE BOTH ON THE SAME TEAM
3. Gives them encouragement for practicing this skill
4. Provides a brief example of how this could lead to a win-win solution

Keep it warm, supportive, and under 4 lines.
                    """
                    
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
                    final_feedback = msg3_reflection

                st.session_state.messages[tab_name].append({"role": "assistant", "content": final_feedback})
                st.session_state.partner_stage = 4
            else:
                if not st.session_state.get("partner_retry", False):
                    st.session_state.partner_retry = True
                    st.session_state.messages[tab_name].append({
                        "role": "assistant",
                        "content": "Try to think about what they might have been worried about or what they really needed in that moment."
                    })
                else:
                    # Move on anyway after retry
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_reflection})
                    st.session_state.partner_stage = 4

            display_chat_history(tab_name)

    # STAGE 4+: Open-ended chat
    elif st.session_state.partner_stage >= 4:
        handle_user_prompt(client, tab_name)

