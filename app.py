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
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="centered"
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
    st.stop()


# Create OpenAI client with API key
client = OpenAI(api_key=api_key)


# -----------------------------
# Session state (memory)
# -----------------------------
# Streamlit reruns app on every interaction
# So we store messages in session_state to persist chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_project_info" not in st.session_state:
    st.session_state.show_project_info = False


# -----------------------------
# Function → AI call with memory
# -----------------------------
def get_ai_response() -> str:
    """
    This function:
    - Reads the full conversation history
    - Sends the entire chat context to OpenAI
    - Returns a context-aware answer
    """

    # Build conversation history text
    conversation = ""

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"
        else:
            conversation += f"Assistant: {msg['content']}\n"

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
You are a helpful healthcare assistant.

Below is the conversation so far:
{conversation}

Respond to the latest user question using previous context if relevant.

Format the answer like this:

### What it is
### What it means
### Why it matters
### Example

Additional rules:
- Be accurate but simple
- Use short paragraphs or bullets
- If the topic is a CPT code, mention where it is commonly used
- If the topic is an insurance term, explain how it affects a patient or bill
- Keep the answer under 180 words unless the user asks for more detail
- Avoid unnecessary jargon
- Use plain English
"""
    )

    return response.output_text


# -----------------------------
# Function → handle user input
# -----------------------------
def handle_user_input(prompt: str):
    """
    Handles:
    - saving user message
    - calling AI with memory
    - saving AI response
    """

    # Save user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show assistant message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking... ⏳"):
            answer = get_ai_response()
            st.markdown(answer)

    # Save assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("📘 About")
    st.markdown("""
This AI assistant helps explain:

- CPT codes
- Insurance terms
- Basic medical billing concepts
""")

    st.markdown("---")
    st.markdown("### Features")
    st.markdown("- Interactive chat")
    st.markdown("- Example buttons")
    st.markdown("- Context-aware responses")
    st.markdown("- Deployed online")

    st.markdown("---")
    st.markdown("### Example topics")
    st.markdown("- 99213")
    st.markdown("- 99222")
    st.markdown("- Deductible")
    st.markdown("- Coinsurance")
    st.markdown("- Prior authorization")

    st.markdown("---")
    st.markdown("### Career value")
    st.markdown("""
This project demonstrates:

- Python app development
- Streamlit UI design
- OpenAI API integration
- Session-based memory
- GitHub + deployment workflow
""")

    if st.button("📌 Show Project Highlights"):
        st.session_state.show_project_info = not st.session_state.show_project_info

    st.markdown("---")
    st.caption("Version 2.0")
    st.caption("Built with Python, Streamlit, and OpenAI")


# -----------------------------
# Header (UI)
# -----------------------------
st.title("🏥 Healthcare AI Assistant")
st.markdown("### 💡 Understand CPT codes & insurance terms instantly")
st.info("👋 Welcome! Ask about CPT codes, insurance terms, or basic medical billing concepts.")
st.warning("⚠️ This tool is for educational purposes only and is not medical, billing, or legal advice.")
st.markdown("---")


# -----------------------------
# Optional project highlights
# -----------------------------
if st.session_state.show_project_info:
    st.markdown("## 📌 Project Highlights")
    st.markdown("""
This project was built to demonstrate how AI can simplify healthcare billing concepts for users.

### What this project shows
- A deployed AI web application
- Secure API key usage with environment variables
- Session-based conversation memory
- Real-time healthcare concept explanation
- GitHub-based deployment workflow

### Interview talking points
- Why Streamlit was used for fast UI development
- Why OpenAI was used for natural language explanation
- How secrets were protected using `.env` and deployment secrets
- How the chatbot was improved using conversation context
""")
    st.markdown("---")


# -----------------------------
# Start new conversation button
# -----------------------------
if st.button("🗑️ Start New Conversation"):
    st.session_state.messages = []
    st.rerun()


# -----------------------------
# Suggested questions
# -----------------------------
st.markdown("### 💬 Suggested questions")
st.markdown("""
- What is CPT 99213?
- How is 99213 different from 99214?
- What is deductible?
- What is coinsurance?
- What is prior authorization?
""")

st.markdown("---")


# -----------------------------
# Example buttons
# -----------------------------
st.markdown("### 🔍 Try examples:")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("99213"):
        handle_user_input("What is CPT 99213?")
        st.rerun()

with col2:
    if st.button("99222"):
        handle_user_input("What is CPT 99222?")
        st.rerun()

with col3:
    if st.button("Deductible"):
        handle_user_input("What is deductible?")
        st.rerun()

with col4:
    if st.button("Coinsurance"):
        handle_user_input("What is coinsurance?")
        st.rerun()

with col5:
    if st.button("Prior Auth"):
        handle_user_input("What is prior authorization?")
        st.rerun()


# -----------------------------
# Display chat history
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -----------------------------
# Chat input (main user input)
# -----------------------------
if prompt := st.chat_input("Ask about CPT codes or medical terms..."):
    handle_user_input(prompt)
    st.rerun()


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("For educational use only. This tool does not replace professional medical, billing, or legal guidance.")
st.caption("Built with ❤️ using Streamlit and OpenAI.")