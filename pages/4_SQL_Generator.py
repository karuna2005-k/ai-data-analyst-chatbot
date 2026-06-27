import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="SQL Generator", page_icon="🗄️", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.1,
)

st.title("🗄️ SQL Generator")
st.caption("Describe what you want in plain English — get SQL instantly")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Your Table Structure")
    table_info = st.text_area(
        "Paste your table names and columns",
        placeholder="""Example:
orders (order_id, customer_id, product, amount, date)
customers (customer_id, name, city, email)""",
        height=200
    )

with col2:
    st.subheader("💬 What do you want?")
    user_question = st.text_area(
        "Describe your query in plain English",
        placeholder="""Example:
Show me total sales per city for last month, ordered by highest sales first""",
        height=200
    )

db_type = st.radio(
    "Database Type",
    ["MySQL", "PostgreSQL", "SQLite", "SQL Server"],
    horizontal=True
)

if st.button("⚡ Generate SQL", type="primary"):
    if not user_question:
        st.warning("Please describe what you want.")
    else:
        with st.spinner("Generating SQL..."):
            prompt = f"""
            Generate a {db_type} SQL query for the following request.
            
            Table Structure:
            {table_info if table_info else "No table structure provided — use reasonable assumptions"}
            
            Request: {user_question}
            
            Provide:
            1. The SQL query (clean, formatted, ready to run)
            2. A brief explanation of what the query does
            3. Any important notes or assumptions made
            """

            response = llm.invoke([
                SystemMessage(content="You are an expert SQL developer. Write clean, efficient, well-commented SQL queries. Always format the SQL properly."),
                HumanMessage(content=prompt)
            ])

            st.markdown("### ⚡ Generated SQL")
            st.markdown(response.content)

            st.download_button(
                label="📥 Download SQL",
                data=response.content,
                file_name="generated_query.sql",
                mime="text/plain"
            )