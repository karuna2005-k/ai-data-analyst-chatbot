import uuid
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px

load_dotenv()

st.set_page_config(page_title="CSV Analyzer", page_icon="📊", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def get_all_sessions():
    result = supabase.table("csv_chat_history")\
        .select("session_id, content, created_at")\
        .order("created_at", desc=True)\
        .execute()
    sessions = {}
    for row in result.data:
        sid = row["session_id"]
        if sid not in sessions:
            sessions[sid] = row["content"][:40] + "..."
    return sessions

def load_history(session_id):
    result = supabase.table("csv_chat_history")\
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
    supabase.table("csv_chat_history").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def clear_session(session_id):
    supabase.table("csv_chat_history")\
        .delete()\
        .eq("session_id", session_id)\
        .execute()

# Initialize session state
if "csv_session_id" not in st.session_state:
    st.session_state.csv_session_id = str(uuid.uuid4())

if "csv_messages" not in st.session_state:
    st.session_state.csv_messages = []

# Sidebar
with st.sidebar:
    st.markdown("### 📊 CSV Analyzer")
    st.markdown("---")

    if st.button("➕ New Chat"):
        st.session_state.csv_session_id = str(uuid.uuid4())
        st.session_state.csv_messages = []
        st.rerun()

    st.markdown("#### Previous Chats")
    sessions = get_all_sessions()
    for sid, preview in sessions.items():
        if st.button(f"🗨️ {preview}", key=sid):
            st.session_state.csv_session_id = sid
            st.session_state.csv_messages = load_history(sid)
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Current Chat"):
        clear_session(st.session_state.csv_session_id)
        st.session_state.csv_messages = []
        st.rerun()

# Main area
st.title("📊 CSV Analyzer")
st.caption("Upload any CSV and ask questions about your data")
st.markdown("---")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')

    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())

    st.markdown("---")
    st.subheader("📈 Quick Chart")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    all_cols = df.columns.tolist()

    if numeric_cols:
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X Axis", all_cols)
        with col2:
            y_axis = st.selectbox("Y Axis", numeric_cols)

        chart_type = st.radio("Chart Type", ["Bar", "Line", "Scatter"], horizontal=True)

        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis)
        else:
            fig = px.scatter(df, x=x_axis, y=y_axis)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 Ask AI About Your Data")

    for msg in st.session_state.csv_messages:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant").write(msg.content)

    user_input = st.chat_input("Ask about your data...")

    if user_input:
        data_context = f"""
        You are a data analyst. Analyze this dataset and answer questions about it.
        Dataset Info:
        - Shape: {df.shape}
        - Columns: {df.columns.tolist()}
        - Data Types: {df.dtypes.to_dict()}
        - First 5 rows: {df.head().to_string()}
        - Basic Stats: {df.describe().to_string()}
        """
        st.session_state.csv_messages.append(HumanMessage(content=user_input))
        st.chat_message("user").write(user_input)
        save_message(st.session_state.csv_session_id, "human", user_input)
        all_messages = [SystemMessage(content=data_context)] + st.session_state.csv_messages
        response = llm.invoke(all_messages)
        st.session_state.csv_messages.append(AIMessage(content=response.content))
        save_message(st.session_state.csv_session_id, "ai", response.content)
        st.chat_message("assistant").write(response.content)

else:
    if st.session_state.csv_messages:
        st.markdown("---")
        st.subheader("🤖 Previous Conversation")
        for msg in st.session_state.csv_messages:
            if isinstance(msg, HumanMessage):
                st.chat_message("user").write(msg.content)
            else:
                st.chat_message("assistant").write(msg.content)
    else:
        st.info("👆 Upload a CSV file to get started")