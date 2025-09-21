#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import time
import json

# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are Zara — a warm, supportive mentor who helps low-income Pakistani women (with limited education and digital exposure) learn how to balance their family and work responsibilities with confidence. You guide them through WhatsApp-style sessions using relatable examples, small practical tips, and encouragement.

This module covers:
- Recognizing and balancing multiple roles (mother, wife, daughter-in-law, businesswoman, etc.).
- Identifying tensions or conflicts between family and work roles.
- Learning small behaviors that bring success in each role.
- Managing time using tools like the Eisenhower Method.
- Delegating and requesting support effectively.
- Building confidence to integrate different roles peacefully.

Your response rules:
- Always respond in English; if user types in another language and it's unclear, say "I didn't understand that. Let's return to today's topic" and gently redirect.
- Always include one simple, relatable example from the life of a Pakistani woman (e.g. a mother balancing stitching orders with school runs, or a wife handling customers while caring for in-laws).
- Keep replies short (max 5 lines), like WhatsApp messages.
- If the user asks about Stress Management, Money Management, or Digital Literacy, kindly say, "That will come in other sessions 😊" and return to the topic.
- If the user asks about unrelated topics (e.g. marriage, politics, religion), gently bring focus back with kindness.
- Be warm, empathetic, supportive — like an older sister helping you step by step but dont be like "hi there".

Now kindly answer the user's question with warmth and clarity.
"""
# -----------------------------
# Attribution Theory System Prompts
# -----------------------------

SUCCESS_REFLECTION_PROMPT = """
You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.  
Your role is to help them reflect on challenges and successes without being too hard on themselves.  

The user should share a situation where they were successful, or reflect on reasons why something didn't go well.  

Your task:  
1. If user shares a success, celebrate warmly.  
   - Reinforce by highlighting what *they did right* (e.g., planning well, staying patient, using support).  
   - Encourage them to see these actions as repeatable strengths.  

2. If user shares a setback, reframe kindly.  
   - Guide them to see if the cause was something "unstable" (temporary, outside their control, like bad timing or unexpected problems).  
   - Reinforce that these challenges don't define their ability.  
   - Give a short, relatable example (e.g., "Sometimes sales drop just because of weather or school exams — not because you're failing.").  

3. If user gives vague/negative self-blame (e.g., "I'm just bad at this"), gently redirect.  
   - Appreciate their honesty.  
   - Show them a kinder interpretation.  
   - Encourage them with one small positive takeaway.  

4. If unrelated, redirect with kindness.  
   - Explain that we're reflecting on their own situations of success or challenge.  
   - Encourage them to think of one small example.  

Keep replies warm, kind, WhatsApp-style, max 5 lines in english.  
Respond ONLY in JSON format like this:  
{"feedback": "That's wonderful! You succeeded because you stayed patient and planned well. These are strengths you can use again in future challenges.", "is_correct": true}  
"""

ATTRIBUTION_ANALYSIS_PROMPT = """
You are acting as Zara, a warm, supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.  
Your role is to help them interpret success and failure in kinder, more constructive ways.  

The user should reflect on the *causes* behind their success and failure.  

Your task:  
1. If user attributes success to an **internal + stable** factor (e.g., patience, discipline, good planning), celebrate warmly.  
   - Reinforce this as a strength they can always rely on.  
   - Give a short example (e.g., "Because you planned meals well, the family stayed happy — and you can keep doing this again.").  

2. If user attributes success to external or unstable causes (e.g., luck, others' help, timing), still appreciate.  
   - Gently guide them to also notice their own role or effort.  

3. If user reflects on failure:  
   - Help them see if the cause was external/unstable (e.g., electricity outage, market closed).  
   - Reframe so they don't blame themselves too harshly.  
   - Highlight one thing they could learn or improve next time.  

4. If user is vague, negative, or self-blaming (e.g., "I'm useless"), redirect with kindness.  
   - Appreciate honesty.  
   - Suggest one kinder interpretation.  
   - Give a relatable example from Pakistani women's lives (e.g., "Sometimes sales drop only because of weather — not because you failed.").  

5. If unrelated, kindly redirect them to think of a success or failure situation.  

Keep replies warm, kind, WhatsApp-style, max 5 lines in english.  
Respond ONLY in JSON format like this:  
{"feedback": "You linked your success to patience and discipline — that's a stable strength you can trust again and again!", "is_correct": true}  
"""

# -----------------------------
# Pre-scripted conversation messages following the exact flow
# -----------------------------

msg_success_prompt = """Let's look at you again: Think about a situation in which you were successful.

Go ahead!"""

msg_attribution_prompt = """Now think about how you interpreted this: What causes did you attribute your success to?"""

msg_stable_internal_question = """Was this a cause that can be traced back to yourself and is stable?"""

msg_perfect_response = """Perfect! That was a good interpretation!"""

msg_rethink_prompt = """Please think about a possible cause that can be traced back to yourself and is stable."""

msg_failure_prompt = """Well done! Now think about a situation in which you experienced failure."""

# -----------------------------
# Session Setup
# -----------------------------
def setup_session_state_solutions(tab_name: str):
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    if "attribution_stage" not in st.session_state:
        st.session_state.attribution_stage = 0
    if "success_shared" not in st.session_state:
        st.session_state.success_shared = False
    if "attribution_given" not in st.session_state:
        st.session_state.attribution_given = False
    if "stable_internal_confirmed" not in st.session_state:
        st.session_state.stable_internal_confirmed = False

# -----------------------------
# Show chat history
# -----------------------------
def display_chat_history_solutions(tab_name: str):
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -----------------------------
# Open-ended LLM chat for random questions
# -----------------------------
def handle_open_ended_conversation_solutions(client, tab_name: str, user_input: str):
    """Handle random questions during training using the open-ended prompt"""
    try:
        open_ended_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=open_ended_messages,
            stream=False,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return "⚠️ I'm having trouble understanding right now. Let's continue with our lesson about balancing your different roles."

# -----------------------------
# Check if user input is off-topic
# -----------------------------
def is_off_topic_question_solutions(user_input: str) -> bool:
    """Check if the user's input is a random question unrelated to the current stage"""
    off_topic_keywords = [
        "what is", "how to", "tell me about", "explain", "why", "when", 
        "stress management", "money management", "digital literacy", "branding",
        "marriage", "politics", "religion", "weather", "food", "prayer", "namaz",
        "health", "doctor", "medicine"
    ]
    
    user_lower = user_input.lower()
    return any(keyword in user_lower for keyword in off_topic_keywords)

# -----------------------------
# Evaluate responses using specific prompts
# -----------------------------
def evaluate_with_prompt_solutions(client, user_input: str, prompt_type: str):
    """Evaluate user responses using specific system prompts"""
    
    if prompt_type == "success_reflection":
        system_prompt = SUCCESS_REFLECTION_PROMPT
    elif prompt_type == "attribution_analysis":
        system_prompt = ATTRIBUTION_ANALYSIS_PROMPT
    else:
        return {"feedback": "Thank you for sharing that with me.", "is_correct": True}
    
    try:
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User's response: {user_input}"}
            ],
            stream=False,
        )
        raw_feedback = response.choices[0].message.content.strip()
        result = json.loads(raw_feedback)
        return result
        
    except Exception as e:
        return {"feedback": "Thank you for sharing that with me.", "is_correct": True}

# -----------------------------
# MAIN RENDER FUNCTION
# -----------------------------
def render_solutions(client):
    tab_name = "Reflection"
    st.header("Building Confidence Through Success Attribution")

    setup_session_state_solutions(tab_name)
    display_chat_history_solutions(tab_name)

    # tab_name = "Reflection"

    # if tab_name not in st.session_state["messages"]:
    #     st.session_state["messages"][tab_name] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # if "reflection_stage" not in st.session_state:
    #     st.session_state["reflection_stage"] = 0

    # STAGE 0: Ask for success story
    if st.session_state.attribution_stage == 0:
        if not any(msg["content"] == msg_success_prompt for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_success_prompt})
            display_chat_history_solutions(tab_name)
        
        st.session_state.attribution_stage = 1

    # STAGE 1: Collect success story
    elif st.session_state.attribution_stage == 1:
        user_input = st.chat_input("Share a situation where you were successful:")
        if user_input:
            # Check if it's an off-topic question
            if is_off_topic_question_solutions(user_input):
                open_ended_response = handle_open_ended_conversation_solutions(client, tab_name, user_input)
                st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": open_ended_response})
                display_chat_history_solutions(tab_name)
                return
            
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Evaluate success story
            result = evaluate_with_prompt_solutions(client, user_input, "success_reflection")
            feedback = result.get("feedback", "Thank you for sharing that with me.")
            
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_attribution_prompt})
            st.session_state.attribution_stage = 2
            
            display_chat_history_solutions(tab_name)

    # STAGE 2: Ask about attribution causes
    elif st.session_state.attribution_stage == 2:
        user_input = st.chat_input("What causes did you attribute your success to?")
        if user_input:
            # Check if it's an off-topic question
            if is_off_topic_question_solutions(user_input):
                open_ended_response = handle_open_ended_conversation_solutions(client, tab_name, user_input)
                st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": open_ended_response})
                display_chat_history_solutions(tab_name)
                return
            
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_stable_internal_question})
            st.session_state.attribution_stage = 3
            
            display_chat_history_solutions(tab_name)

    # STAGE 3: Check if attribution is stable and internal
    elif st.session_state.attribution_stage == 3:
        user_input = st.chat_input("Was this cause traced back to yourself and stable? (Yes/No)")
        if user_input:
            # Check if it's an off-topic question
            if is_off_topic_question_solutions(user_input):
                open_ended_response = handle_open_ended_conversation_solutions(client, tab_name, user_input)
                st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": open_ended_response})
                display_chat_history_solutions(tab_name)
                return
            
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Check if they answered Yes or No
            if "yes" in user_input.lower() or "haan" in user_input.lower():
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_perfect_response})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_failure_prompt})
                st.session_state.attribution_stage = 5  # Skip to failure stage
            else:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_rethink_prompt})
                st.session_state.attribution_stage = 4
            
            display_chat_history_solutions(tab_name)

    # STAGE 4: Help them think of stable internal causes
    elif st.session_state.attribution_stage == 4:
        user_input = st.chat_input("Think of a cause that can be traced back to yourself and is stable:")
        if user_input:
            # Check if it's an off-topic question
            if is_off_topic_question_solutions(user_input):
                open_ended_response = handle_open_ended_conversation_solutions(client, tab_name, user_input)
                st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": open_ended_response})
                display_chat_history_solutions(tab_name)
                return
            
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Evaluate their stable internal attribution
            result = evaluate_with_prompt_solutions(client, user_input, "attribution_analysis")
            feedback = result.get("feedback", "That's a good way to think about it!")
            
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg_failure_prompt})
            st.session_state.attribution_stage = 5
            
            display_chat_history_solutions(tab_name)

    # STAGE 5: Ask about failure situation
    elif st.session_state.attribution_stage == 5:
        user_input = st.chat_input("Think about a situation where you experienced failure:")
        if user_input:
            # Check if it's an off-topic question
            if is_off_topic_question_solutions(user_input):
                open_ended_response = handle_open_ended_conversation_solutions(client, tab_name, user_input)
                st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": open_ended_response})
                display_chat_history_solutions(tab_name)
                return
            
            st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
            
            # Evaluate failure attribution
            result = evaluate_with_prompt_solutions(client, user_input, "attribution_analysis")
            feedback = result.get("feedback", "Thank you for being honest about that experience.")
            
            st.session_state.messages[tab_name].append({"role": "assistant", "content": feedback})
            
            # Final encouragement message
            final_message = """Great work! You're learning to see your successes as coming from your own strengths (like patience, planning, hard work) and your setbacks as temporary challenges, not permanent failures.

This way of thinking will help you balance your different roles with more confidence. Remember: your successes show your real abilities! 💪"""
            
            st.session_state.messages[tab_name].append({"role": "assistant", "content": final_message})
            st.session_state.attribution_stage = 6
            
            display_chat_history_solutions(tab_name)

    # STAGE 6+: Open-ended chat about role integration
    elif st.session_state.attribution_stage >= 6:
        if prompt := st.chat_input("Chat with Zara (Role Integration)"):
            st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    # Use the updated system prompt for open-ended conversation
                    current_messages = st.session_state.messages[tab_name].copy()
                    current_messages[0] = {"role": "system", "content": SYSTEM_PROMPT}
                    
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=current_messages,
                        stream=True,
                    )
                    response = st.write_stream(stream)
                except Exception as e:
                    response = f"⚠️ Error: {e}"
                    st.error(response)
            st.session_state.messages[tab_name].append({"role": "assistant", "content": response})