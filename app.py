# Import os so we can read environment variables like OPENAI_API_KEY
import os

# Import Streamlit to build the web app UI
import streamlit as st

# Import load_dotenv so Python can read values from a local .env file
from dotenv import load_dotenv

# Import the OpenAI client so the app can call the model
from openai import OpenAI


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
# This sets the browser tab title, icon, and layout width.
# It should be called near the top before most Streamlit UI elements.
st.set_page_config(
    page_title="Healthcare AI Assistant",   # Browser tab title
    page_icon="🏥",                         # Browser tab icon
    layout="wide"                           # Use wide layout for a more professional website feel
)


# -------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------------------------
# This loads values from the .env file into the environment.
# Example from .env:
# OPENAI_API_KEY=your_key_here
load_dotenv()

# Read the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# If the key is missing, show an error and stop the app safely
if not api_key:
    st.error("OPENAI_API_KEY not found. Add it to your .env file.")
    st.stop()

# Create the OpenAI client using the secure API key
client = OpenAI(api_key=api_key)


# -------------------------------------------------
# CUSTOM CSS STYLING
# -------------------------------------------------
# This injects custom CSS into the Streamlit page to make it look more
# polished and more like a professional website.
st.markdown(
    """
    <style>
    /* Main page background spacing adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Large page title styling */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        color: #1f2937;
    }

    /* Subtitle styling */
    .sub-title {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1rem;
    }

    /* Reusable feature card styling */
    .feature-card {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background-color: #f9fafb;
        margin-bottom: 1rem;
        min-height: 120px;
    }

    /* Section title styling */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #111827;
    }

    /* Small muted helper text */
    .small-note {
        font-size: 0.9rem;
        color: #6b7280;
    }

    /* Hero badge styling */
    .hero-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background-color: #e0f2fe;
        color: #0369a1;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# BUILT-IN CPT QUICK LOOKUP DATA
# -------------------------------------------------
# This local dictionary lets the app answer some common CPT code questions
# instantly without always calling the AI model.
# Benefits:
# - faster response time
# - reduced API usage
# - more healthcare-specific behavior
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


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
# Streamlit reruns the script on every interaction.
# session_state is used to preserve data between reruns.

# Store full chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store whether the project highlights section is visible
if "show_project_info" not in st.session_state:
    st.session_state.show_project_info = False

# Store the last assistant answer for copy-ready display
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""


# -------------------------------------------------
# HELPER FUNCTION: FORMAT LOCAL CPT DATA
# -------------------------------------------------
# This function converts local CPT lookup data into a clean markdown format
# that matches the style of AI responses.
def format_cpt_lookup(code: str) -> str:
    # Get the CPT data for the given code
    data = CPT_LOOKUP[code]

    # Return a well-structured markdown response
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


# -------------------------------------------------
# HELPER FUNCTION: COMPARE CPT CODES
# -------------------------------------------------
# This creates a side-by-side comparison between two known CPT codes.
def compare_cpt_codes(code1: str, code2: str) -> str:
    # Read data for both codes
    data1 = CPT_LOOKUP[code1]
    data2 = CPT_LOOKUP[code2]

    # Return comparison in markdown format
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


# -------------------------------------------------
# HELPER FUNCTION: GET AI RESPONSE WITH MEMORY
# -------------------------------------------------
# This function sends the full conversation history to OpenAI,
# so the assistant can answer using context from earlier questions.
def get_ai_response() -> str:
    # Start with an empty conversation string
    conversation = ""

    # Convert session messages into plain text conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"
        else:
            conversation += f"Assistant: {msg['content']}\n"

    # Send the full conversation to OpenAI
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

    # Return only the model's text response
    return response.output_text


# -------------------------------------------------
# HELPER FUNCTION: HANDLE USER INPUT
# -------------------------------------------------
# This function:
# - saves the user's message
# - decides whether to use local CPT data, CPT comparison, or AI
# - displays and stores the assistant response
def handle_user_input(prompt: str):
    # Save the user's message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Clean the prompt for easier CPT detection
    cleaned_prompt = prompt.strip().upper().replace("CPT", "").strip()

    # Create the assistant chat container
    with st.chat_message("assistant"):
        # Show a spinner while generating response
        with st.spinner("Thinking... ⏳"):

            # If the user entered an exact CPT code in local lookup, use local data
            if cleaned_prompt in CPT_LOOKUP:
                answer = format_cpt_lookup(cleaned_prompt)

            # If both 99213 and 99214 are mentioned, show comparison
            elif "99213" in cleaned_prompt and "99214" in cleaned_prompt:
                answer = compare_cpt_codes("99213", "99214")

            # Otherwise, use AI response with memory
            else:
                answer = get_ai_response()

            # Show the answer in the app
            st.markdown(answer)

            # Save latest answer separately for copy-ready display
            st.session_state.last_answer = answer

    # Save assistant response to conversation history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
# The sidebar gives the app structure and makes it feel more like a real website.
with st.sidebar:
    # Sidebar title
    st.title("🏥 Healthcare AI Assistant")

    # Version label
    st.caption("Professional Day 13+ Version")

    # Sidebar divider
    st.markdown("---")

    # About section
    st.markdown("### 📘 About")
    st.markdown("""
This AI assistant helps explain:

- CPT codes  
- Insurance terms  
- Basic medical billing concepts  
""")

    # Sidebar divider
    st.markdown("---")

    # Features section
    st.markdown("### ✨ Features")
    st.markdown("""
- Interactive chat  
- Context-aware responses  
- Built-in CPT quick lookup  
- CPT comparison  
- Suggested questions  
- Copy-ready latest response  
- Professional deployment  
""")

    # Sidebar divider
    st.markdown("---")

    # How to use section
    st.markdown("### 🧭 How to use")
    st.markdown("""
1. Ask about a CPT code or insurance term  
2. Use quick buttons for easy testing  
3. Ask follow-up questions for context-aware answers  
4. Use **Start New Conversation** to reset chat  
""")

    # Sidebar divider
    st.markdown("---")

    # Interview help section
    st.markdown("### 💼 Interview talking points")
    st.markdown("""
- Why Streamlit? Fast UI development  
- Why OpenAI? Natural language explanation  
- Why `.env`? Secret protection  
- Why local CPT lookup? Faster and more domain-specific  
- Why session state? Memory across reruns  
""")

    # Sidebar divider
    st.markdown("---")

    # Career value section
    st.markdown("### 🚀 Career value")
    st.markdown("""
This project demonstrates:

- Python app development  
- Streamlit UI design  
- OpenAI API integration  
- Session-based memory  
- Hybrid app design (local data + AI)  
- GitHub + cloud deployment  
""")

    # Button to show/hide highlights
    if st.button("📌 Show Project Highlights"):
        st.session_state.show_project_info = not st.session_state.show_project_info

    # Sidebar divider
    st.markdown("---")

    # Footer branding in sidebar
    st.caption("Built with Python, Streamlit, and OpenAI")


# -------------------------------------------------
# HERO / HEADER SECTION
# -------------------------------------------------
# Create two columns for a more modern landing section
hero_left, hero_right = st.columns([2.5, 1])

with hero_left:
    # Show a small badge above title
    st.markdown('<div class="hero-badge">AI-Powered Healthcare Learning Tool</div>', unsafe_allow_html=True)

    # Main title
    st.markdown('<div class="main-title">Healthcare AI Assistant</div>', unsafe_allow_html=True)

    # Subtitle
    st.markdown(
        '<div class="sub-title">Understand CPT codes, insurance terms, and medical billing concepts with a professional, interactive AI experience.</div>',
        unsafe_allow_html=True
    )

with hero_right:
    # Helpful callout box
    st.info("👋 Ask a question or use the quick actions below.")

# Professional disclaimer
st.warning("⚠️ This tool is for educational purposes only and is not medical, billing, or legal advice.")

# Divider line
st.markdown("---")


# -------------------------------------------------
# PROJECT VALUE SECTION
# -------------------------------------------------
# This section makes the app feel like a portfolio-ready product.
st.markdown('<div class="section-title">🚀 What this project demonstrates</div>', unsafe_allow_html=True)

# Create three feature cards side by side
demo_col1, demo_col2, demo_col3 = st.columns(3)

with demo_col1:
    st.markdown(
        """
        <div class="feature-card">
        <b>AI + Healthcare</b><br><br>
        Explains CPT codes and insurance terms in simple, user-friendly language.
        </div>
        """,
        unsafe_allow_html=True
    )

with demo_col2:
    st.markdown(
        """
        <div class="feature-card">
        <b>Hybrid Product Design</b><br><br>
        Uses local CPT quick lookup plus AI for broader and smarter answers.
        </div>
        """,
        unsafe_allow_html=True
    )

with demo_col3:
    st.markdown(
        """
        <div class="feature-card">
        <b>Deployment Workflow</b><br><br>
        Built with secure secrets, GitHub version control, and cloud deployment.
        </div>
        """,
        unsafe_allow_html=True
    )

# Divider line
st.markdown("---")


# -------------------------------------------------
# OPTIONAL PROJECT HIGHLIGHTS SECTION
# -------------------------------------------------
# This appears only when the user clicks the sidebar toggle button.
if st.session_state.show_project_info:
    # Section heading
    st.markdown("## 📌 Project Highlights")

    # Description of project value
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

    # Resume summary block
    st.markdown("### Resume Summary")
    st.code(
        "Built and deployed a Healthcare AI Assistant using Python, Streamlit, and OpenAI API with session-based memory, local CPT quick lookup, CPT comparison, and interactive chat UI."
    )

    # Divider line
    st.markdown("---")


# -------------------------------------------------
# TOP ACTION BAR
# -------------------------------------------------
# Create columns for action button and helper note
action_col1, action_col2 = st.columns([1, 3])

with action_col1:
    # Button to clear conversation
    if st.button("🗑️ Start New Conversation"):
        # Clear saved chat messages
        st.session_state.messages = []

        # Clear copy-ready latest response
        st.session_state.last_answer = ""

        # Rerun app so the cleared state is reflected immediately
        st.rerun()

with action_col2:
    # Helper note next to the action button
    st.markdown('<div class="small-note">Use this button to reset chat history and start fresh.</div>', unsafe_allow_html=True)

# Divider line
st.markdown("---")


# -------------------------------------------------
# SUGGESTED QUESTIONS
# -------------------------------------------------
# This section helps first-time users know what to ask.
st.markdown('<div class="section-title">💬 Suggested questions</div>', unsafe_allow_html=True)
st.markdown("""
- What is CPT 99213?  
- How is 99213 different from 99214?  
- What is deductible?  
- What is coinsurance?  
- What is prior authorization?  
""")

# Divider line
st.markdown("---")


# -------------------------------------------------
# QUICK EXAMPLE BUTTONS
# -------------------------------------------------
# These buttons let users test the app quickly without typing.
st.markdown('<div class="section-title">🔍 Quick examples</div>', unsafe_allow_html=True)

# Create five columns for example buttons
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


# -------------------------------------------------
# POPULAR CPT LOOKUP
# -------------------------------------------------
# This is a quick access area for common CPT codes in your local lookup.
st.markdown('<div class="section-title">📊 Popular CPT Codes</div>', unsafe_allow_html=True)

# Create three columns for CPT lookup buttons
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


# -------------------------------------------------
# CPT COMPARISON TOOLS
# -------------------------------------------------
# These buttons support structured CPT comparison and explanation.
st.markdown('<div class="section-title">⚖️ CPT Comparison Tools</div>', unsafe_allow_html=True)

# Create two columns for comparison-related buttons
ccol1, ccol2 = st.columns(2)

with ccol1:
    if st.button("Compare 99213 vs 99214"):
        handle_user_input("Compare CPT 99213 and CPT 99214")
        st.rerun()

with ccol2:
    if st.button("Explain 99214 in simple terms"):
        handle_user_input("Explain CPT 99214 in simple terms")
        st.rerun()

# Divider line
st.markdown("---")


# -------------------------------------------------
# CONVERSATION SECTION
# -------------------------------------------------
# This displays the saved chat history.
st.markdown('<div class="section-title">🧠 Conversation</div>', unsafe_allow_html=True)

# Loop through every saved message and show it in chat format
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------
# Main input area where the user types a question.
if prompt := st.chat_input("Ask about CPT codes or medical terms..."):
    handle_user_input(prompt)
    st.rerun()


# -------------------------------------------------
# COPY-READY LATEST RESPONSE
# -------------------------------------------------
# This displays the latest answer in a code-style block
# so it is easy to copy and reuse.
if st.session_state.last_answer:
    st.markdown("---")
    st.markdown('<div class="section-title">📋 Latest Response (Copy Ready)</div>', unsafe_allow_html=True)
    st.code(st.session_state.last_answer, language=None)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------
# Final footer content for professionalism and compliance.
st.markdown("---")
st.caption("For educational use only. This tool does not replace professional medical, billing, or legal guidance.")
st.caption("Built with ❤️ using Streamlit and OpenAI.")