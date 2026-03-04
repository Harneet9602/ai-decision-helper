import streamlit as st
from groq import Groq
import os

# --- Configuration ---
st.set_page_config(page_title="AI Decision Helper", page_icon="⚖️", layout="centered")

# --- API Setup ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    st.error("⚠️ Groq API Key not found. Please set it in `.streamlit/secrets.toml` or as an environment variable.")
    st.stop()

client = Groq(api_key=API_KEY)

# --- System Prompt & Model Setup ---
system_instruction = """
You are a warm, excited, and expert decision-making assistant. You love helping people gain clarity!
Keep your tone encouraging and conversational, but do not use too many emojis (maximum 1 or 2 per message).
Be concise and clear.
"""

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Components ---
st.title("⚖️ AI Decision Helper")
st.markdown("Stuck on a choice? Tell me what you're deciding between, and we can talk it through!")

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("What decision are you trying to make? Or ask a follow-up!"):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # FIRST message logic
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
        gemini_prompt = prompt

    # --- Send to Groq ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:

                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": gemini_prompt}
                    ],
                )

                response = completion.choices[0].message.content

                st.markdown(response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                st.error(f"An error occurred: {e}")
