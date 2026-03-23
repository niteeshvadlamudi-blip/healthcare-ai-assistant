import streamlit as st
from openai import OpenAI

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY not found. Add it to your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# Setup


st.title("🏥 Healthcare AI Assistant")
st.markdown("### 💡 Explain CPT codes & insurance terms instantly")

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []

# logic
def handle_user_input(prompt):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking... ⏳"):
            response = client.responses.create(
                model="gpt-5-mini",
                input=f"""
You are a healthcare assistant.

Explain clearly in sections:
1. What it is (simple)
2. What it means
3. Why it matters
4. Example

User question: {prompt}
"""
            )
            answer = response.output_text
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# Example buttons
st.markdown("### Try examples:")


if st.button("99213"):
    handle_user_input("99213")

if st.button("99222"):
    handle_user_input("99222")

if st.button("Deductible"):
    handle_user_input("Deductible")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Ask about CPT codes or medical terms..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... ⏳"):
            response = client.responses.create(
                model="gpt-5-mini",
                input=f"""
You are a healthcare assistant.

Explain clearly in sections:
1. What it is (simple)
2. What it means
3. Why it matters
4. Example

User question: {prompt}
"""
            )
            answer = response.output_text
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})