import streamlit as st
import time
import json

# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) better understand and manage stress and build self-confidence in their entrepreneurial journey. You guide them through WhatsApp-style sessions using relatable examples, emotional validation, and simple tools like breathing exercises and daily reflection.

IN THIS MODULE WE TEACH THIS:
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

msg1_stressors_question = """Now please answer this question: What are your three most common personal stressors at work? Type them here in the chat so we can look at them together."""

msg2_stress_education = """Great work! Now you know what your own stress points (stressors) are.

Remember—stress is not always bad. When we feel stress, our body gives us extra energy and focus to handle a problem.

Stress only becomes harmful if it stays for many days or weeks. Too much stress can make you sick, in your mind or your body, and it can reduce your work power. But if you learn to manage stress, it can actually make you stronger and help you reach big goals!"""

msg3_resources_intro = """Let's take a look at what resources you have for dealing with a stressful situation. Remember: resources are your tools for finding a good solution!

You can have two kinds of resources (things that help you):
1. Around you (environment): for example, friends or family who can help you or support you.
2. Inside you (yourself): for example, being good at planning, staying calm, or giving yourself breaks when you need them.

Now think about what helps you when things get stressful. Please write your answers here in the chat so we can look at them together."""

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
    if "stressors_stage" not in st.session_state:
        st.session_state.stressors_stage = 0
    if "user_stressors" not in st.session_state:
        st.session_state.user_stressors = ""
    if "user_resources" not in st.session_state:
        st.session_state.user_resources = ""
    if "stressors_retry_count" not in st.session_state:
        st.session_state.stressors_retry_count = 0
    if "resources_retry_count" not in st.session_state:
        st.session_state.resources_retry_count = 0

# -----------------------------
# Show chat history
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
    if prompt := st.chat_input("Chat with Zara (Personal Stressors & Resources)"):
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
    tab_name = "Personal Stressors & Resources"
    st.header("Identifying Your Stressors and Coping Resources")
    
    setup_session_state(tab_name)
    display_chat_history(tab_name)
    
    # STAGE 0: Present stressors question
    if st.session_state.stressors_stage == 0:
        if not any(msg["content"] == msg1_stressors_question for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1_stressors_question})
            with st.chat_message("assistant"):
                st.markdown(msg1_stressors_question)
        st.session_state.stressors_stage = 1
        st.rerun()
    
    # STAGE 1: Collect user's personal stressors
    elif st.session_state.stressors_stage == 1:
        user_input = st.chat_input("What are your three most common work stressors?")
        if user_input:
            st.session_state.user_stressors = user_input
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Evaluate the user's stressors response
            system_prompt = """
            You are Zara — a warm, supportive mentor who helps low-income Pakistani women understand and manage stress. You are evaluating if a user has identified their personal work stressors effectively.
            
            Your task:
            1. If the user provides THREE specific, work-related stressors (e.g., "customers not paying on time", "too many orders", "family interrupting work"), consider it fully correct.
            - Acknowledge all three stressors warmly
            - Validate their feelings about these stressors
            - Briefly mention how common these are for women entrepreneurs
            
            2. If the user provides 1-2 stressors but they are work-related and specific, consider it acceptable.
            - Appreciate what they shared
            - Validate their stressors
            - Don't ask for more
            
            3. If the user gives very vague answers, only one word, or completely unrelated responses, consider it needs improvement.
            - First, try to make sense of their answer. Often they will give vague responses, so gently suggest a possible meaning. If you still don’t understand, say kindly that you don’t fully understand what they mean — but do not be rude.
            - Explain what a "work stressor" means with simple examples
            
            Be warm, empathetic, supportive — like an older sister. Keep responses short (max 5 lines).
            
            Respond ONLY in JSON format like this:
            {"feedback": "I can see these things really stress you at work! Family interruptions are so common for women like us.", "is_correct": true}
            """
            
            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"User's stressors: {user_input}"}
                    ],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "")
                is_correct = result.get("is_correct", False)
                
            except Exception as e:
                feedback = "Let me help you think about work stressors."
                is_correct = False
            
            with st.chat_message("assistant"):
                st.markdown(feedback)
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            
            if is_correct:
                # Move to education about stress
                with st.chat_message("assistant"):
                    st.markdown(msg2_stress_education)
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2_stress_education})
                
                with st.chat_message("assistant"):
                    st.markdown(msg3_resources_intro)
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_resources_intro})
                
                st.session_state.stressors_stage = 2
            else:
                # Allow retry - increment retry count but stay in same stage
                st.session_state.stressors_retry_count += 1
                
                # Give supportive clarification after first failed attempt
                if st.session_state.stressors_retry_count == 1:
                    clarification = "Can you share a specific moment at work when you felt this stress, for example handling an order or dealing with a customer?"
                    with st.chat_message("assistant"):
                        st.markdown(clarification)
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": clarification})
                
                # After 2 attempts, move forward anyway with encouragement
                if st.session_state.stressors_retry_count >= 2:
                    encouragement = "That's okay! Let's not get stuck here. Let's continue."
                    
                    with st.chat_message("assistant"):
                        st.markdown(encouragement)
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": encouragement})
                    
                    with st.chat_message("assistant"):
                        st.markdown(msg2_stress_education)
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2_stress_education})
                    
                    with st.chat_message("assistant"):
                        st.markdown(msg3_resources_intro)
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3_resources_intro})
                    
                    st.session_state.stressors_stage = 2
            st.rerun()
    
    # STAGE 2: Collect user's coping resources
    elif st.session_state.stressors_stage == 2:
        user_input = st.chat_input("What helps you when things get stressful?")
        if user_input:
            st.session_state.user_resources = user_input
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Evaluate the user's resources response
            system_prompt = """
            You are Zara — a warm, supportive mentor helping Pakistani women identify their coping resources for stress management.
            
            The user should identify resources that help them cope with stress. These can be:
            1. People who support them (family, friends, neighbors)
            2. Personal strengths or skills (staying calm, planning, taking breaks)
            3. Activities that help them feel better (prayer, walking, talking to someone)
            
            Your task:
            1. If user mentions specific helpful resources/people/activities, consider it correct.
            - Celebrate their self-awareness
            - Highlight how these resources make them strong
            
            2. If user gives vague or very brief answers, provide gentle guidance.
            - Appreciate what they shared
            - Give examples to help them think more specifically
            
            3. If user gives completely unrelated responses, guide them back.
            -First, try to make sense of their answer. Often they will give vague responses, so gently suggest a possible meaning. If you still don’t understand, say kindly that you don’t fully understand what they mean — but do not be rude.            - Explain what resources means with examples
            - Ask them to think about what helps them feel better during tough times
            
            Be warm and encouraging. Keep responses short (max 5 lines).
            
            Respond ONLY in JSON format like this:
            {"feedback": "Beautiful! Having your family's support is a powerful resource for managing stress!", "is_correct": true}
            """
            
            try:
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"User's coping resources: {user_input}"}
                    ],
                    stream=False,
                )
                raw_feedback = response.choices[0].message.content.strip()
                result = json.loads(raw_feedback)
                feedback = result.get("feedback", "Thank you for sharing your thoughts.")
                is_correct = result.get("is_correct", False)
                
            except Exception as e:
                feedback = "Thank you for sharing your thoughts about what helps you."
                is_correct = False
            
            with st.chat_message("assistant"):
                st.markdown(feedback)
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            
            if is_correct:
                # Provide final reflection
                final_message = """Perfect! Now you understand your stressors AND your resources. 

Remember: When stress comes, you can use your resources to handle it better. This is how you build confidence - by knowing your own strengths and support system!

Feel free to ask me anything more about managing stress in your work life."""
                
                with st.chat_message("assistant"):
                    st.markdown(final_message)
                st.session_state.messages[tab_name].append({"role": "assistant", "content": final_message})
                st.session_state.stressors_stage = 3
            else:
                # Allow retry
                st.session_state.resources_retry_count += 1
                
                # After 2 attempts, move forward with encouragement
                if st.session_state.resources_retry_count >= 2:
                    final_message = """That's okay! The important thing is that you're learning to think about what helps you.

Remember: We all have resources - people who support us and strengths inside us. When stress comes, try to remember these resources.

Feel free to ask me anything more about managing stress!"""
                    
                    with st.chat_message("assistant"):
                        st.markdown(final_message)
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": final_message})
                    st.session_state.stressors_stage = 3
            
            st.rerun()
    
    # STAGE 3+: Open-ended chat about stress management
    elif st.session_state.stressors_stage >= 3:
        handle_user_prompt(client, tab_name)