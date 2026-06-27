import streamlit as st

st.set_page_config(
    page_title="DataMind AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 DataMind AI")
st.subheader("Your AI-Powered Data Analytics Suite")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("💬 **AI Chat**\nAsk any data analytics question")
    st.info("📊 **CSV Analyzer**\nUpload data, get instant insights")

with col2:
    st.info("💼 **Job Suite**\nATS score + cover letter generator")
    st.info("🗄️ **SQL Generator**\nEnglish to SQL instantly")

with col3:
    st.info("📝 **Data Story**\nAuto business report from your data")
    st.info("🎯 **Interview Prep**\nMock interviews with AI feedback")

st.markdown("---")
st.caption("Built by Karuna Gehani | Powered by Groq + LangChain")