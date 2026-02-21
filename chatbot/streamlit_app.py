import streamlit as st
from chatbot.chatbot import GeminiChatbot



st.set_page_config(page_title="AI Chatbot", page_icon="🤖")

st.title("🤖 Momou AI Assistant")
st.caption("Model: gemini-2.5-flash")



if "bot" not in st.session_state:
    try:
        st.session_state.bot = GeminiChatbot()
    except Exception as e:
        st.error(f"Initialization Error: {str(e)}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if prompt := st.chat_input("Ask me anything..."):

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = st.session_state.bot.chat(prompt)
            except Exception as e:
                reply = f" Error: {str(e)}"

            st.markdown(reply)

    # Store assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
