import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Data Story", page_icon="📝", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.5,
)

st.title("📝 Data Story Generator")
st.caption("Upload your CSV and get a complete business report written by AI")
st.markdown("---")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

report_type = st.radio(
    "Report Type",
    ["Executive Summary", "Detailed Business Report", "Key Insights Only", "Recommendations Only"],
    horizontal=True
)

audience = st.radio(
    "Target Audience",
    ["CEO/Management", "Data Team", "Marketing Team", "General"],
    horizontal=True
)

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')

    st.subheader("📋 Data Preview")
    st.dataframe(df.head(5))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())

    if st.button("📝 Generate Report", type="primary"):
        with st.spinner("AI is writing your report..."):
            prompt = f"""
            You are a senior data analyst writing a {report_type} for {audience}.
            
            Dataset Information:
            - Shape: {df.shape}
            - Columns: {df.columns.tolist()}
            - Data Types: {df.dtypes.to_dict()}
            - Basic Statistics: {df.describe().to_string()}
            - First 10 rows: {df.head(10).to_string()}
            - Missing Values per column: {df.isnull().sum().to_dict()}
            
            Write a professional {report_type} that includes:
            1. Dataset Overview
            2. Key Findings and Patterns
            3. Important Numbers and Metrics
            4. Business Implications
            5. Recommendations
            
            Write in a clear, professional narrative style. Use specific numbers from the data.
            """

            response = llm.invoke([
                SystemMessage(content="You are a senior data analyst and business intelligence expert. Write clear, insightful, data-driven reports."),
                HumanMessage(content=prompt)
            ])

            st.markdown("### 📊 Your Data Story")
            st.markdown(response.content)

            st.download_button(
                label="📥 Download Report",
                data=response.content,
                file_name="data_story_report.txt",
                mime="text/plain"
            )
else:
    st.info("👆 Upload a CSV file to generate your data story")