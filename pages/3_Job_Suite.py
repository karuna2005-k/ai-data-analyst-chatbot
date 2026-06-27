import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Job Suite", page_icon="💼", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
)

st.title("💼 Job Suite AI")
st.caption("Paste your resume and job description to get ATS score, missing keywords, and a cover letter")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    resume_text = st.text_area("Paste your resume text here", height=300)

with col2:
    st.subheader("🎯 Job Description")
    jd_text = st.text_area("Paste the job description here", height=300)

st.markdown("---")

action = st.radio(
    "What do you want?",
    ["ATS Score + Missing Keywords", "Rewrite Resume Bullets", "Generate Cover Letter", "Full Analysis"],
    horizontal=True
)

if st.button("🚀 Analyze", type="primary"):
    if not resume_text or not jd_text:
        st.warning("Please paste both your resume and the job description.")
    else:
        with st.spinner("AI is analyzing..."):

            if action == "ATS Score + Missing Keywords":
                prompt = f"""
                Compare this resume with the job description and give:
                1. ATS Match Score (out of 100)
                2. Top 10 missing keywords from the resume that are in the JD
                3. Top 5 strengths of this resume for this role
                4. Top 3 improvements needed

                Resume: {resume_text}
                Job Description: {jd_text}
                """

            elif action == "Rewrite Resume Bullets":
                prompt = f"""
                Rewrite the resume bullet points to better match this job description.
                Make them more impactful, quantified, and ATS friendly.
                Keep the same experiences but improve the language.

                Resume: {resume_text}
                Job Description: {jd_text}
                """

            elif action == "Generate Cover Letter":
                prompt = f"""
                Write a professional cover letter for this job based on the resume.
                Make it personalized, confident, and under 300 words.
                Do not use generic phrases like "I am writing to express my interest".

                Resume: {resume_text}
                Job Description: {jd_text}
                """

            else:
                prompt = f"""
                Give a complete job application analysis:
                1. ATS Match Score (out of 100)
                2. Top 10 missing keywords
                3. Top 5 strengths
                4. Rewritten resume bullets (top 5)
                5. A short cover letter (under 200 words)
                6. Final recommendation

                Resume: {resume_text}
                Job Description: {jd_text}
                """

            response = llm.invoke([
                SystemMessage(content="You are an expert career coach and ATS optimization specialist."),
                HumanMessage(content=prompt)
            ])

            st.markdown("### 📊 Analysis Result")
            st.markdown(response.content)

            st.download_button(
                label="📥 Download Result",
                data=response.content,
                file_name="job_analysis.txt",
                mime="text/plain"
            )