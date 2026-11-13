"""LeetResume.AI: Agentic Career Co-Pilot | Purdue LeetCode Club workshop."""
import io
import os
import re
import time
from pathlib import Path

os.environ.setdefault("OTEL_SDK_DISABLED", "true")  # keep CrewAI telemetry quiet

import streamlit as st
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

BASE_URL = os.getenv("PURDUE_GENAI_BASE_URL", "https://genai.purdue.edu/api/v1")
API_KEY = os.getenv("PURDUE_GENAI_API_KEY")
DEFAULT_MODEL = os.getenv("GENAI_MODEL_NAME", "openai/gpt-4o")
SAMPLE_DIR = Path(__file__).parent / "sample_data"
SAMPLE_PDF = SAMPLE_DIR / "sample_swe_resume.pdf"
SAMPLE_JD = SAMPLE_DIR / "sample_swe_internship_posting.txt"
# Verify these IDs against the GenAI Studio model catalog before the event.
MODELS = list(dict.fromkeys(
    [DEFAULT_MODEL, "openai/gpt-4o", "openai/claude-3-5-sonnet", "openai/llama-3.1-70b"]
)) + ["Custom..."]

st.set_page_config(page_title="LeetResume.AI", page_icon="📄", layout="wide")

CSS = """
<style>
.hero{background:linear-gradient(135deg,#000 0%,#2b2b2b 100%);border-left:8px solid #CFB991;
      padding:1.2rem 1.6rem;border-radius:12px;margin-bottom:1rem}
.hero h1{color:#CFB991;margin:0;font-size:2rem}
.hero p{color:#ddd;margin:.3rem 0 0}
.chip{display:inline-block;padding:2px 10px;margin:2px;border-radius:999px;font-size:.8rem;font-weight:600}
.chip.ok{background:#1b5e20;color:#fff}
.chip.miss{background:#b71c1c;color:#fff}
.chip.new{background:#CFB991;color:#000}
</style>
"""

# Display name -> regex. Used for a fast, local keyword check (no LLM needed).
KEYWORDS = {
    "Python": r"python", "Java": r"java(?!script)", "C++": r"c\+\+", "Go": r"(?-i:Go)|golang",
    "JavaScript": r"javascript", "TypeScript": r"typescript", "SQL": r"sql",
    "PostgreSQL": r"postgres(?:ql)?", "React": r"react", "Flask": r"flask", "Django": r"django",
    "REST APIs": r"restful|rest\s+apis?", "Docker": r"docker", "Kubernetes": r"kubernetes|k8s",
    "Terraform": r"terraform", "AWS": r"aws|amazon web services", "GCP": r"gcp|google cloud",
    "Azure": r"azure", "CI/CD": r"ci\s*/\s*cd", "GitHub Actions": r"github actions",
    "Git": r"git", "Linux": r"linux", "Agile": r"agile|scrum", "Microservices": r"microservices?",
    "Unit Testing": r"unit[\s-]?test(?:s|ing)?",
}


def keyword_scan(text: str) -> set:
    return {k for k, p in KEYWORDS.items()
            if re.search(rf"(?<![\w+#])(?:{p})(?![\w+#])", text, re.I)}


def chips(items, kind: str) -> str:
    body = " ".join(f'<span class="chip {kind}">{i}</span>' for i in sorted(items))
    return body or "<em>None</em>"


@st.cache_data(show_spinner=False)
def extract_pdf(data: bytes):
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        reader.decrypt("")
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(p for p in pages if p.strip()), len(reader.pages)


def get_llm(model: str, temperature: float):
    # TODO 1: return LLM(model=model, base_url=BASE_URL, api_key=API_KEY, temperature=temperature)
    # Tip: decorate with @st.cache_resource so Streamlit reruns reuse one client.
    raise NotImplementedError("TODO 1: initialize the LLM")


def run_pipeline(llm, resume_text, job_desc, role_type, tone, sections, max_bullets, on_step):
    """Critic -> Writer. Returns (critique_markdown, rewrite_markdown)."""
    # TODO 2: create critic_agent and writer_agent
    #   Agent(role=..., goal=..., backstory=..., llm=llm, verbose=False, allow_delegation=False)
    # TODO 3: create task_critique and task_rewrite
    #   Task(description=..., expected_output=..., agent=...)
    #   Give task_rewrite context=[task_critique] so the writer sees the audit.
    # TODO 4: assemble Crew(agents=[...], tasks=[...], process=Process.sequential),
    #   call .kickoff(), then return (critique_text, rewrite_text) from output.tasks_output[i].raw
    raise NotImplementedError("TODOs 2-4: build the agents, tasks, and crew")


# ---------- Sidebar ----------
def load_sample():
    st.session_state.use_sample = True
    st.session_state.job_desc = SAMPLE_JD.read_text() if SAMPLE_JD.exists() else ""


def reset_all():
    for key in ("use_sample", "job_desc", "result"):
        st.session_state.pop(key, None)


st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    if API_KEY:
        st.success("API key loaded from .env")
    else:
        st.error("Missing PURDUE_GENAI_API_KEY. Check your .env file.")
    st.caption(f"Gateway: {BASE_URL}")

    choice = st.selectbox("Model", MODELS)
    model = st.text_input("Custom model ID", value="openai/") if choice == "Custom..." else choice
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.05,
                            help="Lower = more literal and consistent. Higher = more varied phrasing.")

    if st.button("🔌 Test connection"):
        with st.spinner("Pinging the gateway..."):
            try:
                reply = get_llm(model, temperature).call("Reply with the single word: OK")
                st.success(f"Connected. Model replied: {str(reply)[:60]}")
            except Exception as exc:
                st.error(f"Connection failed: {str(exc)[:300]}")

    st.divider()
    st.subheader("✍️ Rewrite options")
    role_type = st.selectbox("Target role type",
                             ["Software Engineering", "Cloud / DevOps", "Cybersecurity", "Data / ML"])
    tone = st.radio("Tone", ["Concise & technical", "Balanced", "Impact-focused"], index=1)
    sections = st.multiselect("Sections to rewrite",
                              ["Experience", "Projects", "Leadership & Activities", "Skills"],
                              default=["Experience", "Projects"])
    max_bullets = st.slider("Max bullets per role/project", 2, 5, 3)

    st.divider()
    st.button("📂 Load sample data", on_click=load_sample, help="Uses files in sample_data/")
    st.button("🗑️ Reset", on_click=reset_all)

# ---------- Header ----------
st.markdown(
    '<div class="hero"><h1>📄 LeetResume.AI</h1>'
    "<p>Agentic Career Co-Pilot · Purdue LeetCode Club Workshop · Powered by Purdue GenAI Studio</p></div>",
    unsafe_allow_html=True,
)
with st.expander("ℹ️ How the pipeline works"):
    st.markdown(
        "1. **Extract:** `pypdf` pulls the text out of your resume PDF.\n"
        "2. **Agent 1, ATS Critic:** compares your resume to the job description and writes a gap analysis.\n"
        "3. **Agent 2, Technical Writer:** receives that analysis as context and rewrites your bullets "
        "with the Google XYZ formula: *Accomplished [X] as measured by [Y], by doing [Z]*.\n\n"
        "The writer is told never to invent metrics. Missing numbers show up as `[N]` placeholders for you to fill in."
    )

stepper = st.container()

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("1. Candidate Resume")
        uploaded = st.file_uploader("Upload PDF Resume", type=["pdf"])
        resume_bytes, source = None, ""
        if uploaded:
            resume_bytes, source = uploaded.getvalue(), uploaded.name
        elif st.session_state.get("use_sample") and SAMPLE_PDF.exists():
            resume_bytes, source = SAMPLE_PDF.read_bytes(), "sample_swe_resume.pdf (sample)"

        resume_text, pages = "", 0
        if resume_bytes:
            try:
                resume_text, pages = extract_pdf(resume_bytes)
            except Exception as exc:
                st.error(f"Could not read this PDF: {exc}")
        if resume_text:
            c1, c2, c3 = st.columns(3)
            c1.metric("Pages", pages)
            c2.metric("Words", len(resume_text.split()))
            c3.metric("Source", "Sample" if "sample" in source else "Upload")
            with st.expander("Preview extracted text"):
                st.text(resume_text[:5000])
            if len(resume_text) < 200:
                st.warning("Very little text was extracted. Is this a scanned PDF? Export from Docs or Word instead.")
        elif resume_bytes:
            st.warning("No text found. The PDF may be an image scan.")

with col2:
    with st.container(border=True):
        st.subheader("2. Target Position")
        job_desc = st.text_area("Paste Job Description (SWE, DevOps, Security, etc.)",
                                key="job_desc", height=250)
        jd_words = len(job_desc.split())
        st.caption(f"{jd_words} words" + ("  ·  ⚠️ Very long, consider trimming." if jd_words > 1500 else ""))
        jd_kw = keyword_scan(job_desc)
        if jd_kw:
            with st.expander(f"Detected requirements ({len(jd_kw)})"):
                st.markdown(chips(jd_kw, "new"), unsafe_allow_html=True)

# ---------- Pre-flight keyword check (local, instant) ----------
res_kw = keyword_scan(resume_text)
if resume_text and jd_kw:
    with st.container(border=True):
        st.subheader("🎯 Pre-flight keyword check")
        matched, missing = jd_kw & res_kw, jd_kw - res_kw
        st.progress(len(matched) / len(jd_kw), text=f"{len(matched)} of {len(jd_kw)} job keywords found in your resume")
        k1, k2 = st.columns(2)
        k1.markdown("**✅ Already on your resume**", help="Keywords found in both")
        k1.markdown(chips(matched, "ok"), unsafe_allow_html=True)
        k2.markdown("**❌ Missing from your resume**")
        k2.markdown(chips(missing, "miss"), unsafe_allow_html=True)

# ---------- Run ----------
has_jd = jd_words >= 30
ready = bool(resume_text) and has_jd and bool(API_KEY) and bool(sections)
with stepper:
    s1, s2, s3 = st.columns(3)
    s1.markdown(f"{'✅' if resume_text else '⬜'} **Resume loaded**")
    s2.markdown(f"{'✅' if has_jd else '⬜'} **Job description added**")
    s3.markdown(f"{'✅' if 'result' in st.session_state else '⬜'} **Optimized**")

run = st.button("🚀 Optimize Resume", type="primary", disabled=not ready)
if not ready:
    todo = [t for t, ok in [("upload a resume", resume_text), ("paste a job description (30+ words)", has_jd),
                            ("set your API key in .env", API_KEY), ("pick at least one section", sections)] if not ok]
    st.caption("To continue: " + ", ".join(todo) + ".")

if run:
    st.session_state.pop("result", None)
    with st.status("Running multi-agent pipeline...", expanded=True) as status:
        try:
            st.write(f"📄 Parsed {pages} page(s). Starting **{model}** at temperature {temperature}.")
            st.write("🕵️ Agent 1 (ATS Critic) is auditing your resume...")
            started = time.time()
            critique, rewrite = run_pipeline(
                get_llm(model, temperature), resume_text, job_desc, role_type,
                tone, sections, max_bullets, on_step=st.write,
            )
            before = res_kw & jd_kw
            after = (res_kw | keyword_scan(rewrite)) & jd_kw
            st.session_state.result = {
                "critique": critique, "rewrite": rewrite, "seconds": time.time() - started,
                "model": model, "before": before, "after": after, "total": len(jd_kw),
                "original": resume_text,
            }
            status.update(label="Optimization complete", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Pipeline failed", state="error")
            st.error(f"{type(exc).__name__}: {str(exc)[:500]}")
            st.info("Common fixes: check the API key and model ID, retry if the request timed out, "
                    "or use 'Test connection' in the sidebar.")

# ---------- Results (kept in session_state so reruns don't wipe them) ----------
res = st.session_state.get("result")
if res:
    st.divider()
    st.header("Results")
    total = max(res["total"], 1)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Keyword coverage before", f"{len(res['before']) / total:.0%}")
    m2.metric("Estimated coverage after", f"{len(res['after']) / total:.0%}",
              delta=f"{(len(res['after']) - len(res['before'])) / total:+.0%}")
    m3.metric("Run time", f"{res['seconds']:.0f}s")
    m4.metric("Model", res["model"].split("/")[-1])

    tab_gap, tab_new, tab_cmp, tab_exp = st.tabs(
        ["🔍 ATS Gap Analysis", "✍️ Rewritten Resume", "↔️ Compare", "⬇️ Export"])
    with tab_gap:
        st.markdown(res["critique"])
    with tab_new:
        newly = res["after"] - res["before"]
        if newly:
            st.markdown("**Newly covered keywords:** " + chips(newly, "new"), unsafe_allow_html=True)
        st.markdown(res["rewrite"])
    with tab_cmp:
        left, right = st.columns(2)
        left.subheader("Original")
        left.text(res["original"])
        right.subheader("Revised")
        right.markdown(res["rewrite"])
    with tab_exp:
        st.download_button("⬇️ Revised resume (.md)", res["rewrite"], "revised_resume.md", "text/markdown")
        st.download_button("⬇️ Gap analysis (.md)", res["critique"], "gap_analysis.md", "text/markdown")
        st.caption("Copy-ready Markdown:")
        st.code(res["rewrite"], language="markdown")

st.divider()
st.caption("Always review AI output before sending it. Replace every [N] placeholder with a real number, "
           "or delete the claim.")
