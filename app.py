import streamlit as st
import google.generativeai as genai
import os

# --- Configuration ---
st.set_page_config(page_title="AI Decision Helper", page_icon="⚖️", layout="centered")

# --- API Setup ---
API_KEY = "AIzaSyBzfElHgqt0jEGyinaUS_xOwRBNL8h_VLk"

if not API_KEY:
    st.error("⚠️ Gemini API Key not found. Please set it in `.streamlit/secrets.toml` or as an environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- System Prompt & Model Setup ---
# We use system instructions to give the AI its personality and rules.
system_instruction = """
You are a warm, excited, and expert decision-making assistant. You love helping people gain clarity!
Keep your tone encouraging and conversational, but do not use too many emojis (maximum 1 or 2 per message). 
Be concise and clear.
"""

# Initialize the model with the system instruction
model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction=system_instruction
)

# --- Session State Management ---
# 1. Store the Gemini chat object to maintain conversational history
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 2. Store the UI messages so they don't disappear when Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Components ---
st.title("⚖️ AI Decision Helper")
st.markdown("Stuck on a choice? Tell me what you're deciding between, and we can talk it through!")

# Display previous messages from the session state
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input & Logic ---
# st.chat_input automatically pins to the bottom of the screen
if prompt := st.chat_input("What decision are you trying to make? Or ask a follow-up!"):
    
    # 1. Display the user's message in the UI immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Save it to the UI history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Determine if this is the FIRST message or a FOLLOW-UP
    # If it's the first message, wrap it in our strict formatting rules.
    if len(st.session_state.messages) == 1:
        gemini_prompt = f"""
        The user needs help with the following decision: "{prompt}"
        
        Please analyze this decision and provide your response STRICTLY in the following Markdown format:
        
        ### Pros of Option A
        * [Pro 1]
        * [Pro 2]
        
        ### Pros of Option B
        * [Pro 1]
        * [Pro 2]
        
        ### Key Factors to Consider
        * [Factor 1]
        * [Factor 2]
        
        ### Recommendation
        [State a clear, single recommendation]
        
        ### Short Reasoning
        [Briefly explain why based on the factors]
        """
    else:
        # If it's a follow-up, just send the prompt naturally
        gemini_prompt = prompt

    # 4. Send the prompt to Gemini and display the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_session.send_message(gemini_prompt)
                st.markdown(response.text)
                
                # Save the assistant's response to the UI history
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
