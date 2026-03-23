# Import os → used to read environment variables like API key
import os

# Import Streamlit → used to build the web UI
import streamlit as st

# Import dotenv → used to load variables from .env file
from dotenv import load_dotenv

# Import OpenAI client → used to call GPT model
from openai import OpenAI


# -----------------------------
# Page configuration
# -----------------------------
# Sets browser tab title, icon and layout
# Must be one of the FIRST Streamlit commands
st.set_page_config(
    page_title="Healthcare AI Assistant",   # browser tab name
    page_icon="🏥",                         # emoji icon
    layout="centered"                       # page layout (centered content)
)


# -----------------------------
# Load environment variables
# -----------------------------
# Loads variables from .env file into Python
load_dotenv()

# Fetch API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Safety check → stops app if key is missing
if not api_key:
    st.error("OPENAI_API_KEY not found. Add it to your .env file.")
    st.stop()  # stops app execution completely


# Create OpenAI client with API key
client = OpenAI(api_key=api_key)


# -----------------------------
# Session state (memory)
# -----------------------------
# Streamlit reruns app on every interaction
# So we store messages in session_state to persist chat

if "messages" not in st.session_state:
    st.session_state.messages = []  # initialize empty chat history


# -----------------------------
# Function → AI call
# -----------------------------
def get_ai_response(prompt: str) -> str:
    """
    This function:
    - Sends user input to OpenAI
    - Gets response from model
    - Returns clean output text
    """

    response = client.responses.create(
        model="gpt-5-mini",  # lightweight fast model

        # Prompt sent to model
        input=f"""
You are a helpful healthcare assistant.

Explain the user's question clearly in these sections:
1. What it is (simple)
2. What it means
3. Why it matters
4. Example

Rules:
- Keep it easy to understand
- Avoid heavy medical jargon
- Keep answer under 200 words

User question: {prompt}
"""
    )

    # Extract only text output from response object
    return response.output_text


# -----------------------------
# Function → handle user input
# -----------------------------
def handle_user_input(prompt: str):
    """
    Handles:
    - saving user message
    - calling AI
    - saving AI response
    """

    # Save user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show assistant message container
    with st.chat_message("assistant"):

        # Show loading spinner while AI is processing
        with st.spinner("Thinking... ⏳"):

            # Call AI function
            answer = get_ai_response(prompt)

            # Display response in UI
            st.markdown(answer)

    # Save assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# -----------------------------
# Header (UI)
# -----------------------------
# Main title shown on page
st.title("🏥 Healthcare AI Assistant")

# Subtitle / description
st.markdown("### 💡 Understand CPT codes & insurance terms instantly")

# Horizontal divider line
st.markdown("---")


# -----------------------------
# Clear chat button
# -----------------------------
# Button resets chat history
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []  # clear stored messages
    st.rerun()  # refresh app immediately


# -----------------------------
# Example buttons
# -----------------------------
# Section label
st.markdown("### 🔍 Try examples:")

# Create 3 columns for layout
col1, col2, col3 = st.columns(3)


# Button 1 → CPT code
with col1:
    if st.button("99213"):
        handle_user_input("99213")
        st.rerun()  # refresh UI


# Button 2 → CPT code
with col2:
    if st.button("99222"):
        handle_user_input("99222")
        st.rerun()


# Button 3 → insurance term
with col3:
    if st.button("Deductible"):
        handle_user_input("What is deductible?")
        st.rerun()


# -----------------------------
# Display chat history
# -----------------------------
# Loop through stored messages and show them

for msg in st.session_state.messages:

    # Display message in chat bubble format
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -----------------------------
# Chat input (main user input)
# -----------------------------
# Input box at bottom of screen
if prompt := st.chat_input("Ask about CPT codes or medical terms..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... ⏳"):

            # Call AI
            answer = get_ai_response(prompt)

            # Display response
            st.markdown(answer)

    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# -----------------------------
# Footer
# -----------------------------
# Divider
st.markdown("---")

# Footer text (portfolio branding)
st.markdown("Built with ❤️ using Streamlit and OpenAI")