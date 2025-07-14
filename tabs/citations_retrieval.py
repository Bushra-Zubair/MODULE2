#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Focus on Issues Not People - Communication Training for Female Entrepreneurs – Ferrosa App

WhatsApp-style training to help Pakistani women entrepreneurs learn to focus on problems
rather than people when resolving conflicts with family members.

Adapted on Thu July 11 2025
@author: amna
"""

import streamlit as st
import time
import json


# -----------------------------
# MODEL + SYSTEM PROMPT
# -----------------------------
# DEFAULT_MODEL = "ft:gpt-4o-2024-08-06:iml-research:wakeel:BW4oryHJ"

SYSTEM_PROMPT = """
You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

This training emphasizes that success as an entrepreneur is not just about having the right skills or hustle—it's also deeply connected to the support you receive from your family and social environment. Recognizing and nurturing family support—emotional, practical, and financial—can significantly strengthen your entrepreneurial journey. The training guides participants through three key steps for effective communication with family:

1. Separate people from the problem – Use "I-" and "We-" statements to avoid blame and build empathy.  
2. Focus on interests, not positions – Understand and express both your needs and those of your family members.  
3. Find win-win solutions – Collaborate to develop outcomes that work for everyone, not just one side.

Participants also learn to identify their current support levels, express unmet needs, and practice constructive conversations with family. They explore real-life examples.

Your task:
1. If the user submits a question, answer kindly based **only** on the training content above.
2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
4. Do **not** ask any follow-up questions.
5. Keep your response short (4–5 lines) and suitable for WhatsApp.
6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."
"""

# -----------------------------
# Pre-scripted conversation messages
# -----------------------------
msg1 = (
    "To find solutions to such situations, try to focus on the issue itself and the facts—not on the people involved."
)

msg2 = (
    "Maybe you can relate to this: We often say to others something like \"You always do...\", \"You're always so...\", \"You make me mad when you…\"\n\n"
    "1 - Yes!\n"
    "2 - Maybe"
)

msg3 = (
    "However these kinds of statements usually don't help—they often cause misunderstandings.\n\n"
    "If you want to look at the problem more neutral way, try this:"
)

msg4 = (
    "Use I- and We-statements because they help you focus on the real issue instead of blaming or criticizing the other person.\n\n"
    "Let me show you how it works!\n\n"
    "1 - Let's do it!"
)

msg5 = (
    "**I-Statements** are phrases like: \"I feel...\", \"I think...\", or \"I get upset when...\". They help you share your thoughts and feelings in a clear and respectful way—without blaming the other person.\n\n"
    "1 - Go on"
)

msg6 = (
    "**We-Statements** are phrases like: \"We feel happy when...\", or \"We can work together to find solutions...\" They help you emphasize teamwork and shared goals, which can strengthen your connection with others.\n\n"
    "**If you have any questions related to this training so far, write it in the chat to learn better.**"
)

# -----------------------------
# Session Setup
# -----------------------------
def setup_session_state(tab_name: str):
    # if "openai_model" not in st.session_state:
    #     st.session_state["openai_model"] = DEFAULT_MODEL
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    if "focus_stage" not in st.session_state:
        st.session_state.focus_stage = 0

# -----------------------------
# Show chat history
# -----------------------------
def display_chat_history(tab_name: str):
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -----------------------------
# Handle user questions with LLM
# -----------------------------
def handle_user_question(client, tab_name: str, user_text: str, is_during_training: bool = True):
    """Handle user questions using LLM during the training flow"""
    try:
        # Create different prompts based on whether we're in training or free chat
        if is_during_training:
            question_prompt = f"""
You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

Your task:
1. If the user submits a question, answer kindly based **only** on the training content about communication skills, I-statements, We-statements, and family support.
2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
4. Do **not** ask any follow-up questions.
5. Keep your response short (4–5 lines) and suitable for WhatsApp.
6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."
7. After answering, always end with "Let's go back to where we left off in the training!"

Here is the user's message:
[User question starts]  
{user_text}  
[User question ends]
            """
        else:
            question_prompt = f"""
You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

Your task:
1. If the user submits a question, answer kindly based **only** on the training content about communication skills, I-statements, We-statements, and family support.
2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
4. Do **not** ask any follow-up questions.
5. Keep your response short (4–5 lines) and suitable for WhatsApp.
6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."

Here is the user's message:
[User question starts]  
{user_text}  
[User question ends]
            """
        
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": question_prompt}
            ],
            stream=False,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        if is_during_training:
            return f"⚠️ Sorry, I couldn't process your question right now. Let's go back to where we left off in the training!"
        else:
            return f"⚠️ Sorry, I couldn't process your question right now. Please try again!"

# -----------------------------
# Check if user input is expected training response
# -----------------------------
def is_training_response(user_input: str, expected_stage: int) -> bool:
    """Check if user input matches expected training flow response"""
    user_input = user_input.strip()
    
    if expected_stage == 1:  # Stage 1 expects "1" or "2"
        return user_input in ["1", "2"]
    elif expected_stage in [2, 3]:  # Stages 2 and 3 expect "1"
        return user_input == "1"
    
    return False

# -----------------------------
# Get stage instruction text
# -----------------------------
def get_stage_instruction(stage: int) -> str:
    """Get instruction text for current stage"""
    if stage == 1:
        return "Type 1 or 2 to continue the training, or ask any question!"
    elif stage == 2:
        return "Type 1 to continue the training, or ask any question!"
    elif stage == 3:
        return "Type 1 to continue the training, or ask any question!"
    else:
        return "Ask any questions about this training or chat freely!"

# -----------------------------
# MAIN RENDER FUNCTION
# -----------------------------
def render(client):
    tab_name = "Focus on Issues"
    st.header("Focus on Issues, Not People")

    setup_session_state(tab_name)
    display_chat_history(tab_name)

    # STAGE 0: Show initial messages
    if st.session_state.focus_stage == 0:
        if not any(msg["content"] == msg1 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1})
            st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2})
            st.session_state.focus_stage = 1
            st.rerun()

    # Always show chat input - this is the key change
    current_instruction = get_stage_instruction(st.session_state.focus_stage)
    user_input = st.chat_input(current_instruction)
    
    if user_input:
        # Add user message to chat
        st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
        
        # Check if this is expected training response or a question
        if is_training_response(user_input, st.session_state.focus_stage):
            # Handle training flow progression
            if st.session_state.focus_stage == 1:
                # Both 1 and 2 lead to same message
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3})
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4})
                st.session_state.focus_stage = 2
                
            elif st.session_state.focus_stage == 2:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5})
                st.session_state.focus_stage = 3
                
            elif st.session_state.focus_stage == 3:
                st.session_state.messages[tab_name].append({"role": "assistant", "content": msg6})
                st.session_state.focus_stage = 4
        else:
            # Handle as question/free chat using LLM
            # Check if we're still in training (stages 1-3) or in free chat (stage 4+)
            is_during_training = st.session_state.focus_stage < 4
            response = handle_user_question(client, tab_name, user_input, is_during_training)
            st.session_state.messages[tab_name].append({"role": "assistant", "content": response})
            
            # If we're in training mode, repeat the current training message after answering the question
            if is_during_training:
                if st.session_state.focus_stage == 1:
                    # Repeat the message that expects "1" or "2"
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2})
                elif st.session_state.focus_stage == 2:
                    # Repeat the message that expects "1" to continue
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4})
                elif st.session_state.focus_stage == 3:
                    # Repeat the message that expects "1" to continue
                    st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5})
        
        # Refresh the display
        st.rerun()
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Focus on Issues Not People - Communication Training for Female Entrepreneurs – Ferrosa App

# WhatsApp-style training to help Pakistani women entrepreneurs learn to focus on problems
# rather than people when resolving conflicts with family members.

# Adapted on Thu July 11 2025
# @author: amna
# """

# import streamlit as st
# import time
# import json


# # -----------------------------
# # MODEL + SYSTEM PROMPT
# # -----------------------------
# DEFAULT_MODEL = "ft:gpt-4o-2024-08-06:iml-research:wakeel:BW4oryHJ"

# SYSTEM_PROMPT = """
# You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

# This training emphasizes that success as an entrepreneur is not just about having the right skills or hustle—it's also deeply connected to the support you receive from your family and social environment. Recognizing and nurturing family support—emotional, practical, and financial—can significantly strengthen your entrepreneurial journey. The training guides participants through three key steps for effective communication with family:

# 1. Separate people from the problem – Use "I-" and "We-" statements to avoid blame and build empathy.  
# 2. Focus on interests, not positions – Understand and express both your needs and those of your family members.  
# 3. Find win-win solutions – Collaborate to develop outcomes that work for everyone, not just one side.

# Participants also learn to identify their current support levels, express unmet needs, and practice constructive conversations with family. They explore real-life examples.

# Your task:
# 1. If the user submits a question, answer kindly based **only** on the training content above.
# 2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
# 3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
# 4. Do **not** ask any follow-up questions.
# 5. Keep your response short (4–5 lines) and suitable for WhatsApp.
# 6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."
# """

# # -----------------------------
# # Pre-scripted conversation messages
# # -----------------------------
# msg1 = (
#     "To find solutions to such situations, try to focus on the issue itself and the facts—not on the people involved."
# )

# msg2 = (
#     "Maybe you can relate to this: We often say to others something like \"You always do...\", \"You're always so...\", \"You make me mad when you…\"\n\n"
#     "1 - Yes!\n"
#     "2 - Maybe"
# )

# msg3 = (
#     "However these kinds of statements usually don't help—they often cause misunderstandings.\n\n"
#     "If you want to look at the problem more neutral way, try this:"
# )

# msg4 = (
#     "Use I- and We-statements because they help you focus on the real issue instead of blaming or criticizing the other person.\n\n"
#     "Let me show you how it works!\n\n"
#     "1 - Let's do it!"
# )

# msg5 = (
#     "**I-Statements** are phrases like: \"I feel...\", \"I think...\", or \"I get upset when...\". They help you share your thoughts and feelings in a clear and respectful way—without blaming the other person.\n\n"
#     "1 - Go on"
# )

# msg6 = (
#     "**We-Statements** are phrases like: \"We feel happy when...\", or \"We can work together to find solutions...\" They help you emphasize teamwork and shared goals, which can strengthen your connection with others.\n\n"
#     "**If you have any questions related to this training so far, write it in the chat to learn better.**"
# )

# # -----------------------------
# # Session Setup
# # -----------------------------
# def setup_session_state(tab_name: str):
#     if "openai_model" not in st.session_state:
#         st.session_state["openai_model"] = DEFAULT_MODEL
#     if "messages" not in st.session_state:
#         st.session_state.messages = {}
#     if tab_name not in st.session_state.messages:
#         st.session_state.messages[tab_name] = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ]
#     if "focus_stage" not in st.session_state:
#         st.session_state.focus_stage = 0

# # -----------------------------
# # Show chat history
# # -----------------------------
# def display_chat_history(tab_name: str):
#     for msg in st.session_state.messages[tab_name]:
#         if msg["role"] != "system":
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])

# # -----------------------------
# # Handle user questions with LLM
# # -----------------------------
# def handle_user_question(client, tab_name: str, user_text: str, is_during_training: bool = True):
#     """Handle user questions using LLM during the training flow"""
#     try:
#         # Create different prompts based on whether we're in training or free chat
#         if is_during_training:
#             question_prompt = f"""
# You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

# Your task:
# 1. If the user submits a question, answer kindly based **only** on the training content about communication skills, I-statements, We-statements, and family support.
# 2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
# 3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
# 4. Do **not** ask any follow-up questions.
# 5. Keep your response short (4–5 lines) and suitable for WhatsApp.
# 6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."
# 7. After answering, always end with "Let's go back to where we left off in the training!"

# Here is the user's message:
# [User question starts]  
# {user_text}  
# [User question ends]
#             """
#         else:
#             question_prompt = f"""
# You are acting as Zara, a warm and supportive mentor for Pakistani women entrepreneurs with limited education and digital exposure.

# Your task:
# 1. If the user submits a question, answer kindly based **only** on the training content about communication skills, I-statements, We-statements, and family support.
# 2. If the user asks about **Role Integration, Stress Management, Personal Branding, or Digital Literacy**, kindly inform them that these topics will be covered in future training modules and redirect them back to this module's focus.
# 3. If the question is completely unrelated, respond gently and redirect back to the module's focus (e.g., win-win thinking, expressing interests, asking for support).
# 4. Do **not** ask any follow-up questions.
# 5. Keep your response short (4–5 lines) and suitable for WhatsApp.
# 6. Always respond in English and if you can't decipher the language, just redirect to the topic after saying "I don't understand what you said."

# Here is the user's message:
# [User question starts]  
# {user_text}  
# [User question ends]
#             """
        
#         response = client.chat.completions.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": "system", "content": question_prompt}
#             ],
#             stream=False,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         if is_during_training:
#             return f"⚠️ Sorry, I couldn't process your question right now. Let's go back to where we left off in the training!"
#         else:
#             return f"⚠️ Sorry, I couldn't process your question right now. Please try again!"

# # -----------------------------
# # Check if user input is expected training response
# # -----------------------------
# def is_training_response(user_input: str, expected_stage: int) -> bool:
#     """Check if user input matches expected training flow response"""
#     user_input = user_input.strip()
    
#     if expected_stage == 1:  # Stage 1 expects "1" or "2"
#         return user_input in ["1", "2"]
#     elif expected_stage in [2, 3]:  # Stages 2 and 3 expect "1"
#         return user_input == "1"
    
#     return False

# # -----------------------------
# # Get stage instruction text
# # -----------------------------
# def get_stage_instruction(stage: int) -> str:
#     """Get instruction text for current stage"""
#     if stage == 1:
#         return "Type 1 or 2 to continue the training, or ask any question!"
#     elif stage == 2:
#         return "Type 1 to continue the training, or ask any question!"
#     elif stage == 3:
#         return "Type 1 to continue the training, or ask any question!"
#     else:
#         return "Ask any questions about this training or chat freely!"

# # -----------------------------
# # MAIN RENDER FUNCTION
# # -----------------------------
# def render(client):
#     tab_name = "Focus on Issues"
#     st.header("Focus on Issues, Not People")

#     setup_session_state(tab_name)
#     display_chat_history(tab_name)

#     # STAGE 0: Show initial messages
#     if st.session_state.focus_stage == 0:
#         if not any(msg["content"] == msg1 for msg in st.session_state.messages[tab_name] if msg["role"] == "assistant"):
#             st.session_state.messages[tab_name].append({"role": "assistant", "content": msg1})
#             st.session_state.messages[tab_name].append({"role": "assistant", "content": msg2})
#             st.session_state.focus_stage = 1
#             st.rerun()

#     # Always show chat input - this is the key change
#     current_instruction = get_stage_instruction(st.session_state.focus_stage)
#     user_input = st.chat_input(current_instruction)
    
#     if user_input:
#         # Add user message to chat
#         st.session_state.messages[tab_name].append({"role": "user", "content": user_input})
        
#         # Check if this is expected training response or a question
#         if is_training_response(user_input, st.session_state.focus_stage):
#             # Handle training flow progression
#             if st.session_state.focus_stage == 1:
#                 # Both 1 and 2 lead to same message
#                 st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3})
#                 st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4})
#                 st.session_state.focus_stage = 2
                
#             elif st.session_state.focus_stage == 2:
#                 st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5})
#                 st.session_state.focus_stage = 3
                
#             elif st.session_state.focus_stage == 3:
#                 st.session_state.messages[tab_name].append({"role": "assistant", "content": msg6})
#                 st.session_state.focus_stage = 4
#         else:
#             # Handle as question/free chat using LLM
#             # Check if we're still in training (stages 1-3) or in free chat (stage 4+)
#             is_during_training = st.session_state.focus_stage < 4
#             response = handle_user_question(client, tab_name, user_input, is_during_training)
#             st.session_state.messages[tab_name].append({"role": "assistant", "content": response})
            
#             # If we're in training mode, show the next training message after answering the question
#             if is_during_training:
#                 if st.session_state.focus_stage == 1:
#                     # After answering question in stage 1, continue with stage 1 flow
#                     st.session_state.messages[tab_name].append({"role": "assistant", "content": msg3})
#                     st.session_state.messages[tab_name].append({"role": "assistant", "content": msg4})
#                     st.session_state.focus_stage = 2
#                 elif st.session_state.focus_stage == 2:
#                     # After answering question in stage 2, continue with stage 2 flow
#                     st.session_state.messages[tab_name].append({"role": "assistant", "content": msg5})
#                     st.session_state.focus_stage = 3
#                 elif st.session_state.focus_stage == 3:
#                     # After answering question in stage 3, continue with stage 3 flow
#                     st.session_state.messages[tab_name].append({"role": "assistant", "content": msg6})
#                     st.session_state.focus_stage = 4
        
#         # Refresh the display
#         st.rerun()
 