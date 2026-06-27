import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Interview Prep", page_icon="🎯", layout="wide")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
)

st.title("🎯 Interview Prep")
st.caption("Practice mock interviews with AI feedback on your answers")
st.markdown("---")

role = st.selectbox(
    "Select Job Role",
    ["Data Analyst", "Business Analyst", "Data Scientist", "ML Engineer", "Python Developer", "SQL Developer"]
)

level = st.radio(
    "Experience Level",
    ["Fresher", "1-2 Years", "3-5 Years"],
    horizontal=True
)

question_type = st.radio(
    "Question Type",
    ["Technical", "Behavioral", "SQL", "Python", "Case Study", "Mixed"],
    horizontal=True
)

if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "score_total" not in st.session_state:
    st.session_state.score_total = []

col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Get New Question", type="primary"):
        with st.spinner("Generating question..."):
            prompt = f"""
            Generate 1 {question_type} interview question for a {level} {role} position.
            Make it realistic and commonly asked in Indian tech companies.
            Return only the question, nothing else.
            """
            response = llm.invoke([
                SystemMessage(content="You are an experienced technical interviewer."),
                HumanMessage(content=prompt)
            ])
            st.session_state.current_question = response.content
            st.session_state.interview_messages = []

with col2:
    if st.button("🗑️ Reset Session"):
        st.session_state.interview_messages = []
        st.session_state.current_question = None
        st.session_state.score_total = []
        st.rerun()

if st.session_state.current_question:
    st.markdown("---")
    st.subheader("❓ Question")
    st.info(st.session_state.current_question)

    st.subheader("✍️ Your Answer")
    user_answer = st.text_area("Type your answer here", height=150, key="answer_input")

    if st.button("📊 Evaluate My Answer", type="primary"):
        if not user_answer:
            st.warning("Please type your answer first.")
        else:
            with st.spinner("AI is evaluating your answer..."):
                eval_prompt = f"""
                Interview Question: {st.session_state.current_question}
                Candidate Answer: {user_answer}
                Role: {level} {role}
                
                Evaluate this answer and provide:
                1. Score out of 10
                2. What was good about the answer
                3. What was missing or could be improved
                4. A model answer for comparison
                5. One tip for next time
                """

                response = llm.invoke([
                    SystemMessage(content="You are an expert technical interviewer. Be honest but encouraging in your feedback."),
                    HumanMessage(content=eval_prompt)
                ])

                st.markdown("### 📊 AI Feedback")
                st.markdown(response.content)

                st.session_state.interview_messages.append({
                    "question": st.session_state.current_question,
                    "answer": user_answer,
                    "feedback": response.content
                })

if st.session_state.interview_messages:
    st.markdown("---")
    st.subheader(f"📚 Session History ({len(st.session_state.interview_messages)} questions)")
    for i, item in enumerate(st.session_state.interview_messages):
        with st.expander(f"Q{i+1}: {item['question'][:60]}..."):
            st.markdown(f"**Your Answer:** {item['answer']}")
            st.markdown(f"**Feedback:** {item['feedback']}")