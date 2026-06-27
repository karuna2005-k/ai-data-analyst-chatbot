import uuid
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

system_prompt = "You are an expert data analyst assistant. You help users understand data, statistics, charts, SQL, Python, and business insights in simple clear language."

def load_history(session_id):
    result = supabase.table("chat_history")\
        .select("*")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    messages = []
    for row in result.data:
        if row["role"] == "human":
            messages.append(HumanMessage(content=row["content"]))
        else:
            messages.append(AIMessage(content=row["content"]))
    return messages

def save_message(session_id, role, content):
    supabase.table("chat_history").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def clear_session(session_id):
    supabase.table("chat_history")\
        .delete()\
        .eq("session_id", session_id)\
        .execute()

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = load_history(st.session_state.session_id)

# Sidebar
with st.sidebar:
    st.markdown("### 💬 DataMind AI")
    st.markdown("---")

    if st.button("➕ New Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_messages = []
        st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Current Chat"):
        clear_session(st.session_state.session_id)
        st.session_state.chat_messages = []
        st.rerun()

# Main chat area
st.title("💬 AI Data Analyst Chat")
st.caption("Ask me anything about data, statistics, or business insights")
st.markdown("---")

for msg in st.session_state.chat_messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("Ask your data question...")

if user_input:
    st.session_state.chat_messages.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)
    save_message(st.session_state.session_id, "human", user_input)
    all_messages = [SystemMessage(content=system_prompt)] + st.session_state.chat_messages
    response = llm.invoke(all_messages)
    st.session_state.chat_messages.append(AIMessage(content=response.content))
    save_message(st.session_state.session_id, "ai", response.content)
    st.chat_message("assistant").write(response.content)