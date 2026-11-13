# LeetResume.AI: Agentic Career Co-Pilot

**Purdue LeetCode Club Workshop** · November 17th, 2026 · STEW 314 · 6:00 to 7:30 PM

Build a local multi-agent resume co-pilot with **Python, Streamlit, and CrewAI**, powered by **Purdue GenAI Studio**. Instead of one generic prompt, two specialized AI agents work as a pipeline: an ATS critic audits your resume against a real job posting, then a technical writer rewrites your bullets using the **Google XYZ formula**:

> Accomplished **[X]** as measured by **[Y]**, by doing **[Z]**

---

## What you will build

A Streamlit app that:

- Extracts text from your PDF resume
- Compares it to a job description with an instant local keyword check
- Runs a two-agent CrewAI pipeline (ATS Critic, then Technical Writer)
- Shows a gap analysis, a rewritten resume, a side-by-side comparison, and downloadable Markdown

```
PDF resume + job description
        │
        ▼
 Agent 1: ATS Critic ──(structured diagnostics)──▶ Agent 2: Technical Writer
                                                          │
                                                          ▼
                                              XYZ-formatted Markdown revision
```

**Why agents?** Single-shot prompts tend to produce generic adjectives, fake metrics, and context bleed. Passing the critic's findings to a second agent with its own role and rules gives more focused, honest output. The writer is instructed never to invent metrics. Missing numbers appear as `[N]` placeholders for you to fill in.

---

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | **Starter template.** Full UI, with four `TODO` sections to complete during the workshop. |
| `solution` | **Finished app.** Switch to it if you fall behind: `git checkout solution` |

---

## Prerequisites

- **Python 3.10 or newer** (3.10 to 3.12 is the safest choice)
- **Git**
- A laptop with **VS Code** or **PyCharm**
- A **Purdue Career Account** (SSO/BoilerKey) with access to Purdue GenAI Studio
- Optional: your own resume as a **PDF with real, selectable text** (not a scan) and a job posting you want to target

Check your versions:

```bash
python3 --version   # Windows: python --version
git --version
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/leetresume-ai.git
cd leetresume-ai
```

### 2. Create and activate a virtual environment

**Mac / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the start of your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your Purdue GenAI Studio API token

1. Open Purdue GenAI Studio and log in with your **Purdue Career Account** (SSO/BoilerKey).
2. Go to your account settings and generate an **API key / token**.
3. Copy it. You will paste it in the next step.

> Follow the 2-slide guide from the workshop if you get stuck. Organizers will be circulating during setup.

### 5. Configure your `.env` file

Copy the template:

```bash
cp .env.example .env          # Mac / Linux
copy .env.example .env        # Windows
```

Open `.env` and paste your token:

```
PURDUE_GENAI_BASE_URL="https://genai.purdue.edu/api/v1"
PURDUE_GENAI_API_KEY="paste_your_token_here"
GENAI_MODEL_NAME="openai/gpt-4o"
```

| Variable | Meaning |
| --- | --- |
| `PURDUE_GENAI_BASE_URL` | Purdue's OpenAI-compatible gateway |
| `PURDUE_GENAI_API_KEY` | Your personal token. **Never share or commit it.** |
| `GENAI_MODEL_NAME` | Model ID, with an `openai/` prefix so CrewAI uses the OpenAI-compatible route |

> `.env` is listed in `.gitignore`, so Git will not upload it. Do not paste your token into any other file.

### 6. Run the app

```bash
streamlit run app.py
```

Your browser opens to `http://localhost:8501`. If not, open that address yourself.

---

## Quick start

1. In the sidebar, click **Test connection**. You should see a green "Connected" message.
2. Click **Load sample data** to use the resume and job posting in `sample_data/`, or upload your own PDF and paste a job description.
3. Check the **Pre-flight keyword check** to see which job keywords your resume is missing.
4. Click **Optimize Resume** and watch the two agents work.
5. Review the tabs: **ATS Gap Analysis**, **Rewritten Resume**, **Compare**, and **Export**.
6. Replace every `[N]` placeholder with a real number, or delete the claim.

---

## Workshop timeline (90 minutes)

| Time | Segment |
| --- | --- |
| 00:00 to 00:15 | Core concepts: why single prompts fail, agent roles/goals/backstories/tasks, the two-agent pipeline |
| 00:15 to 00:30 | Setup: clone, virtual environment, install, Purdue GenAI Studio login, `.env` |
| 00:30 to 01:10 | Live coding: the four TODOs below |
| 01:10 to 01:30 | Testing, debugging, wrap-up, roadmap |

### The four TODOs (in `app.py` on `main`)

| TODO | What you write |
| --- | --- |
| **1** | Initialize the CrewAI `LLM` pointed at the Purdue gateway |
| **2** | Create `critic_agent` and `writer_agent` (role, goal, backstory) |
| **3** | Create `task_critique` and `task_rewrite`, passing the critique as context |
| **4** | Assemble the `Crew`, call `.kickoff()`, and return both outputs |

Until you finish them, the app shows a `NotImplementedError` pointing at the next TODO. That is expected.

---

## Project structure

```
leetresume-ai/
├── .env.example          # Template for your local config (safe to commit)
├── .gitignore            # Keeps .env, .venv, and caches out of Git
├── README.md             # You are here
├── app.py                # Streamlit app (starter on main, finished on solution)
├── requirements.txt      # Python dependencies
└── sample_data/
    ├── sample_swe_resume.pdf
    └── sample_swe_internship_posting.txt
```

---

## Features

- **Sidebar controls:** model selection (or a custom model ID), temperature, target role type, tone, sections to rewrite, and max bullets per role
- **Connection test:** verify your token and model before running the full pipeline
- **PDF preview:** page count, word count, and extracted text preview, with a warning for scanned PDFs
- **Pre-flight keyword check:** instant matched and missing technology keywords, with no LLM call
- **Live pipeline status:** progress updates as each agent finishes
- **Results kept across reruns:** results are stored in Streamlit session state
- **Export:** download the revised resume and gap analysis as Markdown

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Missing PURDUE_GENAI_API_KEY` | Make sure `.env` exists (not just `.env.example`), is in the project root, and contains your token. Restart Streamlit after editing it. |
| `401` / authentication error | Token is wrong, expired, or copied with extra spaces or quotes. Generate a new one. |
| `model not found` / `404` | The model ID is not in the GenAI Studio catalog. Pick another model in the sidebar or use **Custom...**. Keep the `openai/` prefix. |
| Request times out or hangs | The gateway may be busy because many people are using it. Wait a few seconds and click **Optimize Resume** again. |
| "No text found" or very little text extracted | The PDF is a scan or screenshot. Export it again from Google Docs or Word. |
| `ModuleNotFoundError` | Your virtual environment is not active, or dependencies are not installed. Activate `.venv` and run `pip install -r requirements.txt`. |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. Or use Command Prompt. |
| `Port 8501 is already in use` | Run `streamlit run app.py --server.port 8502` |
| Results disappear after clicking a widget | Streamlit reruns the whole script on every interaction. This app stores results in `st.session_state` to avoid that. |

Still stuck? Ask an officer in the room or post in the club Discord.

---

## Privacy and responsible use

- Your resume text is sent to Purdue GenAI Studio to generate results. If you are unsure about sharing personal details, use the sample data.
- **Never commit `.env`** or paste your API token into screenshots, chats, or code.
- AI output can be wrong. **Review every bullet.** Never submit a metric, tool, or role that is not true.

---

## Roadmap (ideas to extend after the workshop)

- Local vector retrieval (**RAG**) over a bank of your past projects and achievements
- Automated **LaTeX** compilation of the revised resume (for example, into Jake's template)
- A third agent for cover letters or interview question practice
- Multi-job batch scoring to compare one resume against several postings

---

## Resources

- [CrewAI documentation](https://docs.crewai.com)
- [Streamlit documentation](https://docs.streamlit.io)
- [pypdf documentation](https://pypdf.readthedocs.io)
- Google XYZ formula: *Accomplished [X] as measured by [Y], by doing [Z]*

---

## Contact

Questions about the workshop? Reach the Purdue LeetCode Club on Slack: https://join.slack.com/t/leetcodeclubpurdue/shared_invite/zt-4g8bg07td-zt6gGjfFl8bo7FIxC0Q7eg

Built by the Purdue LeetCode Club.
