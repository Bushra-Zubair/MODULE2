

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
msg1 = """Welcome to the final session of this training! To wrap up, we'll make a quiz that will help reinforce the key concepts and insights we've explored in this training.

Let's start!

Stress arises because your subconscious categorizes a situation as... ? Type in your answer:
1. stupid
2. dangerous  
3. easy-going
4. irrelevant"""

msg2_correct_first_q1 = """Perfect, this is a good alternative!

Saying 'dangerous' fits because stress happens when we see something as a threat or risk, which activates our stress response.

Moving on to the next question..."""

msg2_correct_q1 = """

Saying 'dangerous' fits because stress happens when we see something as a threat or risk, which activates our stress response.

Moving on to the next question..."""

msg2_wrong_q1 = """I think that doesn't quite fit.

Let me explain: Stress happens when our mind sees something as a threat or danger. For example, when Ayesha's customer didn't pay her, her mind saw it as 'dangerous' to her business survival. 

Try again - which option shows stress comes from seeing something as a threat?"""

msg3_q2 = """Stress is a mismatch between... ? Type in your answer:
1. free will and necessity
2. laziness and discipline  
3. demands and resources
4. fun and duty"""

msg4_correct_q2_first = """Perfect, this is a good alternative!

Saying 'demands and resources' is correct because stress happens when what is expected from you is more than what you can handle with your current resources.

Continue"""


msg4_correct_q2 = """

Saying 'demands and resources' is correct because stress happens when what is expected from you is more than what you can handle with your current resources.

Continue"""

msg4_wrong_q2 = """I think that doesn't quite fit.

Let me explain: Stress happens when the demands on you are more than your resources to handle them. Like when Fatima had 10 orders to complete but only 2 days - the demand was too much for her time resources.

Try again - which option shows this mismatch between what's asked of you and what you can give?"""

msg5_completion = """Excellent work! You've completed the stress management quiz. 

You now understand that:
✓ Stress comes from seeing situations as threats
✓ Stress is a mismatch between demands and resources

Remember, when you feel stressed, ask yourself: 'What resources do I have?' and 'How can I see this differently?' 

You're ready to manage stress better in your entrepreneurial journey! 💪"""

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
    if "quiz_stage" not in st.session_state:
        st.session_state.quiz_stage = 0
    if "q1_retry" not in st.session_state:
        st.session_state.q1_retry = False
    if "q2_retry" not in st.session_state:
        st.session_state.q2_retry = False

# -----------------------------
# Show chat history
# -----------------------------
def display_chat_history(tab_name: str):
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -----------------------------
# Freeform LLM chat (after quiz is done)
# -----------------------------
def handle_user_prompt(client, tab_name: str):
    if prompt := st.chat_input("Chat with Zara (Stress Management Quiz)"):
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
    tab_name = "Stress Management Quiz"
    st.header("Stress Management Quiz")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # STAGE 0: Present first question
    if st.session_state.quiz_stage == 0:
        if not any(msg["content"] == msg1 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1})
            display_chat_history(tab_name)
        
        st.session_state.quiz_stage = 1

    # STAGE 1: Handle first question response
    elif st.session_state.quiz_stage == 1:
        user_input = st.chat_input("Type 1, 2, 3, or 4")
        if user_input:
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Check if answer is correct (option 2 = dangerous)
            if user_input.strip() == "2" or "dangerous" in user_input.lower():
                # Correct answer
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2_correct_first_q1})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_q2})
                st.session_state.quiz_stage = 2
            else:
                # Wrong answer
                if not st.session_state.q1_retry:
                    # First attempt wrong - give specific feedback and explanation
                    st.session_state.q1_retry = True
                    wrong_feedback = ""
                    if user_input.strip() == "1":
                        wrong_feedback = "No, 'stupid' isn't correct. Stress isn't about situations being stupid.\n\n"
                    elif user_input.strip() == "3":
                        wrong_feedback = "No, 'easy-going' isn't correct. Easy-going situations don't create stress.\n\n"
                    elif user_input.strip() == "4":
                        wrong_feedback = "No, 'irrelevant' isn't correct. Irrelevant situations don't trigger stress.\n\n"
                    else:
                        wrong_feedback = "I think that doesn't quite fit.\n\n"
                    
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": wrong_feedback + msg2_wrong_q1})
                else:
                    # Second attempt wrong - give specific feedback and correct answer
                    wrong_feedback = ""
                    if user_input.strip() == "1":
                        wrong_feedback = "No, 'stupid' isn't correct. Stress isn't about situations being stupid. "
                    elif user_input.strip() == "3":
                        wrong_feedback = "No, 'easy-going' isn't correct. Easy-going situations don't create stress. "
                    elif user_input.strip() == "4":
                        wrong_feedback = "No, 'irrelevant' isn't correct. Irrelevant situations don't trigger stress. "
                    else:
                        wrong_feedback = "That's not quite right. "
                    
                    st.session_state.messages[tab_name].append({
                        "role": "assistant", 
                        "content": wrong_feedback + "The correct answer is 2. dangerous. " + msg2_correct_q1
                    })
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_q2})
                    st.session_state.quiz_stage = 2
            
            display_chat_history(tab_name)

    # STAGE 2: Handle second question response
    elif st.session_state.quiz_stage == 2:
        user_input = st.chat_input("Type 1, 2, 3, or 4")
        if user_input:
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Check if answer is correct (option 3 = demands and resources)
            if user_input.strip() == "3" or ("demands" in user_input.lower() and "resources" in user_input.lower()):
                # Correct answer
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4_correct_q2_first})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5_completion})
                st.session_state.quiz_stage = 3
            else:
                # Wrong answer
                if not st.session_state.q2_retry:
                    # First attempt wrong - give specific feedback and explanation
                    st.session_state.q2_retry = True
                    wrong_feedback = ""
                    if user_input.strip() == "1":
                        wrong_feedback = "No, 'free will and necessity' isn't correct. This isn't about philosophical concepts.\n\n"
                    elif user_input.strip() == "2":
                        wrong_feedback = "No, 'laziness and discipline' isn't correct. Stress isn't about personal motivation.\n\n"
                    elif user_input.strip() == "4":
                        wrong_feedback = "No, 'fun and duty' isn't correct. This isn't about enjoyment vs obligation.\n\n"
                    else:
                        wrong_feedback = "I think that doesn't quite fit.\n\n"
                    
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": wrong_feedback + msg4_wrong_q2})
                else:
                    # Second attempt wrong - give specific feedback and correct answer
                    wrong_feedback = ""
                    if user_input.strip() == "1":
                        wrong_feedback = "No, 'free will and necessity' isn't correct. This isn't about philosophical concepts. "
                    elif user_input.strip() == "2":
                        wrong_feedback = "No, 'laziness and discipline' isn't correct. Stress isn't about personal motivation. "
                    elif user_input.strip() == "4":
                        wrong_feedback = "No, 'fun and duty' isn't correct. This isn't about enjoyment vs obligation. "
                    else:
                        wrong_feedback = "That's not quite right. "
                    
                    st.session_state.messages[tab_name].append({
                        "role": "assistant", 
                        "content": wrong_feedback + "The correct answer is 3. demands and resources. " + msg4_correct_q2
                    })
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5_completion})
                    st.session_state.quiz_stage = 3
            
            display_chat_history(tab_name)

    # STAGE 3+: Open-ended chat after quiz completion
    elif st.session_state.quiz_stage >= 3:
        handle_user_prompt(client, tab_name)
