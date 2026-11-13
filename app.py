import os
import streamlit as st
from pypdf import PdfReader
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

# Verify Environment Variables
base_url = os.getenv("PURDUE_GENAI_BASE_URL", "https://genai.purdue.edu/api/v1")
api_key = os.getenv("PURDUE_GENAI_API_KEY")

if not api_key:
    st.error("Missing PURDUE_GENAI_API_KEY. Check your local .env configuration.")
    st.stop()

# Initialize LLM via Purdue's Gateway
purdue_llm = LLM(
    model=os.getenv("GENAI_MODEL_NAME", "openai/gpt-4o"),
    base_url=base_url,
    api_key=api_key
)

# Streamlit Page Setup
st.set_page_config(page_title="LeetResume.AI", page_icon="📄", layout="wide")
st.title("LeetResume.AI: Agentic Career Co-Pilot")
st.caption("Purdue LeetCode Club Workshop | Powered by Purdue GenAI Studio")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Candidate Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

with col2:
    st.subheader("2. Target Position")
    job_desc = st.text_area("Paste Job Description (SWE, DevOps, Security, etc.)", height=200)

def extract_pdf_text(file) -> str:
    reader = PdfReader(file)
    extracted = [page.extract_text() for page in reader.pages if page.extract_text()]
    return "\n".join(extracted)

if st.button("Optimize Resume", type="primary") and uploaded_file and job_desc:
    with st.spinner("Extracting content and running multi-agent optimization..."):
        resume_text = extract_pdf_text(uploaded_file)

        # Agent 1: ATS & Technical Screener
        critic_agent = Agent(
            role="Principal Technical Screener & ATS Specialist",
            goal="Identify missing technical proficiencies, keyword gaps, and weak passive phrasing.",
            backstory=(
                "You are an expert technical hiring screener specializing in early-career engineering "
                "and cybersecurity roles. You rigorously score resumes on keyword alignment, impact clarity, "
                "and ATS parsing integrity."
            ),
            llm=purdue_llm,
            verbose=False
        )

        # Agent 2: Technical Resume Strategist
        writer_agent = Agent(
            role="Elite Technical Resume Strategist",
            goal="Rewrite resume bullets using the Google XYZ formula without fabricating technical experience.",
            backstory=(
                "You transform rough technical bullets into high-impact, quantifiable contributions. "
                "You adhere strictly to truthfulness: never fabricate metrics, tools, or roles that the candidate "
                "did not mention. Structure achievements as: Accomplished [X], measured by [Y], by doing [Z]."
            ),
            llm=purdue_llm,
            verbose=False
        )

        # Task 1: Diagnostic Critique
        task_critique = Task(
            description=(
                f"Candidate Resume Content:\n{resume_text}\n\n"
                f"Target Job Description:\n{job_desc}\n\n"
                "Provide a prioritized gap analysis: identify missing critical technologies, "
                "flag bullets lacking measurable metrics, and outline 3 high-impact improvement vectors."
            ),
            expected_output="Bulleted diagnostic audit specifying gaps, missing keywords, and weak phrasing.",
            agent=critic_agent
        )

        # Task 2: Targeted Revision
        task_rewrite = Task(
            description=(
                "Using the ATS Specialist's critique, rewrite all experience and project bullet points. "
                "Ensure every bullet follows the XYZ format, naturally integrates missing target keywords where justifiable, "
                "and formats cleanly in Markdown."
            ),
            expected_output="Complete revised experience and project sections formatted in clean Markdown.",
            agent=writer_agent
        )

        # Pipeline Execution
        career_crew = Crew(
            agents=[critic_agent, writer_agent],
            tasks=[task_critique, task_rewrite],
            verbose=False
        )

        output = career_crew.kickoff()

    st.success("Optimization Complete!")
    st.subheader("Targeted Bullet Revisions")
    st.markdown(output.raw)
