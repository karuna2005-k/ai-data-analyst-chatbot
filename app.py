import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import SystemMessage

from dotenv import load_dotenv
import os
load_dotenv() 

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
)

st.title("My First AI Chatbot")
st.markdown("---")
st.caption("🤖 Powered by Groq + LangChain | Data Analyst Assistant")
st.markdown("---")
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
st.write("Ask me anything!")

system_prompt = "You are a helpful data analyst assistant. You help users understand data, statistics, charts, and business insights in simple language."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)
    
    all_messages = [SystemMessage(content=system_prompt)] + st.session_state.messages
    response = llm.invoke(all_messages)
    
    st.session_state.messages.append(AIMessage(content=response.content))
    st.chat_message("assistant").write(response.content)