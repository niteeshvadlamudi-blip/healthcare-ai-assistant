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
st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="centered"
)


# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY not found. Add it to your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)


# -----------------------------
# Built-in CPT quick lookup
# -----------------------------
# Day 10: local healthcare data for common CPT codes
# Purpose:
# - faster responses for common codes
# - reduces API usage
# - makes app more domain-specific
CPT_LOOKUP = {
    "99213": {
        "what_it_is": "An established patient office or outpatient visit of low-to-moderate complexity.",
        "what_it_means": "This code is commonly used for a follow-up visit when the provider evaluates an ongoing condition.",
        "why_it_matters": "It helps determine billing and reimbursement for a very common outpatient visit.",
        "example": "A patient returns for follow-up on blood pressure and medication review."
    },
    "99214": {
        "what_it_is": "An established patient office or outpatient visit of moderate complexity.",
        "what_it_means": "It is used for follow-up visits requiring more detailed evaluation or management than 99213.",
        "why_it_matters": "It reflects a higher level of work and can affect billing and reimbursement.",
        "example": "A patient with diabetes and hypertension is seen for follow-up and medication adjustments."
    },
    "99222": {
        "what_it_is": "An initial hospital or observation care visit of moderate complexity.",
        "what_it_means": "It is used when a clinician first evaluates a patient admitted for hospital or observation care.",
        "why_it_matters": "It affects hospital billing and documentation requirements.",
        "example": "A patient is admitted for chest pain and the physician performs the first hospital evaluation."
    }
}


# -----------------------------
# Session state (memory)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_project_info" not in st.session_state:
    st.session_state.show_project_info = False

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""


# -----------------------------
# Helper → format local CPT data
# -----------------------------
def format_cpt_lookup(code: str) -> str:
    """
    Converts CPT dictionary data into the same clean output format
    used by the AI responses.
    """
    data = CPT_LOOKUP[code]
    return f"""
### What it is
{data['what_it_is']}

### What it means
{data['what_it_means']}

### Why it matters
{data['why_it_matters']}

### Example
{data['example']}
"""


# -----------------------------
# Helper → compare two CPT codes
# -----------------------------
# Day 11: adds side-by-side structured comparison
def compare_cpt_codes(code1: str, code2: str) -> str:
    """
    Creates a structured comparison between two built-in CPT codes.
    """
    data1 = CPT_LOOKUP[code1]
    data2 = CPT_LOOKUP[code2]

    return f"""
## CPT Code Comparison: {code1} vs {code2}

### {code1}
- **What it is:** {data1['what_it_is']}
- **Meaning:** {data1['what_it_means']}
- **Why it matters:** {data1['why_it_matters']}
- **Example:** {data1['example']}

### {code2}
- **What it is:** {data2['what_it_is']}
- **Meaning:** {data2['what_it_means']}
- **Why it matters:** {data2['why_it_matters']}
- **Example:** {data2['example']}

### Key Difference
{code2} usually represents a more complex or more detailed level of service than {code1}.
"""


# -----------------------------
# Function → AI call with memory
# -----------------------------
def get_ai_response() -> str:
    """
    This function:
    - Reads full conversation history
    - Sends full chat context to OpenAI
    - Returns a context-aware answer
    """

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
    - checking built-in CPT lookup first
    - calling AI if needed
    - saving assistant response
    """

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    cleaned_prompt = prompt.strip().upper().replace("CPT", "").strip()

    with st.chat_message("assistant"):
        with st.spinner("Thinking... ⏳"):

            # Day 10: use local CPT lookup if exact code is known
            if cleaned_prompt in CPT_LOOKUP:
                answer = format_cpt_lookup(cleaned_prompt)

            # Day 11: smart comparison for built-in codes
            elif "99213" in cleaned_prompt and "99214" in cleaned_prompt:
                answer = compare_cpt_codes("99213", "99214")

            else:
                answer = get_ai_response()

            st.markdown(answer)

            # Save latest answer separately so it can be copied easily
            st.session_state.last_answer = answer

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
    st.markdown("- Built-in CPT quick lookup")
    st.markdown("- Deployed online")

    st.markdown("---")
    st.markdown("### Example topics")
    st.markdown("- 99213")
    st.markdown("- 99214")
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
- Hybrid app design (local data + AI)
- GitHub + deployment workflow
""")

    if st.button("📌 Show Project Highlights"):
        st.session_state.show_project_info = not st.session_state.show_project_info

    st.markdown("---")
    st.caption("Version 3.0")
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
- Hybrid CPT quick lookup + AI explanation
- GitHub-based deployment workflow

### Interview talking points
- Why Streamlit was used for fast UI development
- Why OpenAI was used for natural language explanation
- How secrets were protected using `.env` and deployment secrets
- How the chatbot was improved using conversation context
- How local CPT data was combined with AI for better performance
""")
    st.markdown("---")


# -----------------------------
# Start new conversation button
# -----------------------------
if st.button("🗑️ Start New Conversation"):
    st.session_state.messages = []
    st.session_state.last_answer = ""
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
# Popular CPT quick lookup
# -----------------------------
# Day 10: quick access buttons for built-in structured CPTs
st.markdown("### 📊 Popular CPT Codes")
pcol1, pcol2, pcol3 = st.columns(3)

with pcol1:
    if st.button("Lookup 99213"):
        handle_user_input("99213")
        st.rerun()

with pcol2:
    if st.button("Lookup 99214"):
        handle_user_input("99214")
        st.rerun()

with pcol3:
    if st.button("Lookup 99222"):
        handle_user_input("99222")
        st.rerun()


# -----------------------------
# CPT comparison tools
# -----------------------------
# Day 11: adds a simple structured comparison feature
st.markdown("### ⚖️ Compare CPT Codes")
ccol1, ccol2 = st.columns(2)

with ccol1:
    if st.button("Compare 99213 vs 99214"):
        handle_user_input("Compare CPT 99213 and CPT 99214")
        st.rerun()

with ccol2:
    if st.button("Explain 99214 in simple terms"):
        handle_user_input("Explain CPT 99214 in simple terms")
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
# Copy-ready latest response
# -----------------------------
# Day 11: makes it easier to copy latest answer
if st.session_state.last_answer:
    st.markdown("---")
    st.markdown("### 📋 Latest Response (Copy Ready)")
    st.code(st.session_state.last_answer, language=None)


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("For educational use only. This tool does not replace professional medical, billing, or legal guidance.")
st.caption("Built with ❤️ using Streamlit and OpenAI.")