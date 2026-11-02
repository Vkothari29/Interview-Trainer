# 🎯 Interview Trainer Agent

An intelligent, RAG-powered interview preparation agent that generates highly personalized question sets, model answers, improvement tips, and realistic mock interview sessions — tailored to your role, experience level, and resume.

**100% free to run.** Powered by Groq + Google Gemini + ChromaDB.

---

## Features

| Tier | Feature |
|------|---------|
| ✅ MVP | Profile input (name, role, level) |
| ✅ MVP | RAG-powered personalized question generation |
| ✅ MVP | Model answers + improvement tips |
| ✅ MVP | Interactive mock interview mode |
| ✅ Core | Answer evaluation & scoring (5 dimensions) |
| ✅ Core | STAR method coaching |
| ✅ Core | Follow-up questions based on your answer |
| ✅ Core | Resume upload & parsing (PDF/DOCX) |
| ✅ Core | Session assessment & readiness score |
| ✅ Core | Exportable Markdown prep report |

---

## Quick Start

### 1. Install dependencies

```bash
cd interview_trainer
py -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

py -m pip install -r requirements.txt
```

> On Windows use `py` (the Python launcher). If `python` or `streamlit` is
> not on your PATH, use `py` / `py -m streamlit` instead.

### 2. Set up API keys

```bash
copy .env.example .env
# Edit .env and add your keys:
#   GROQ_API_KEY=...       (https://console.groq.com — free)
#   GOOGLE_API_KEY=...     (https://aistudio.google.com — free, optional)
```

### 3. Build the knowledge base (optional)

```bash
py knowledge_base/rag_store.py
```

The vector store is also built automatically on first use.

### 4. Run the app

The complete app is the Flask app:

```bash
py run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

The older Streamlit UI is still available as an optional alternative:

```bash
py -m streamlit run app.py
# http://localhost:8501
```

---

## Project Structure

```
interview_trainer/
├── run.py                          # Flask entry point
├── app/                            # Flask app (routes, templates, services)
├── app.py                          # Optional Streamlit UI
├── requirements.txt
├── .env.example
├── knowledge_base/
│   ├── questions_seed.json         # Curated Q&A seed dataset
│   └── rag_store.py                # ChromaDB vector store + retrieval
├── tools/
│   ├── resume_parser.py            # PDF/DOCX resume extraction + LLM parsing
│   ├── question_generator.py       # RAG + LLM personalized question generation
│   └── evaluator.py                # Answer scoring, STAR coaching, session assessment
├── agent/
│   └── coach_agent.py              # LangGraph state machine + InterviewSession manager
└── data/
    ├── chroma_db/                  # Persistent vector store (auto-created)
    └── flask_sessions/             # Server-side Flask sessions
```

---

## Architecture

```
User (Flask UI, or optional Streamlit)
      ↓
InterviewSession (coach_agent.py)
      ↓
  LangGraph State Machine
      ├── start_session  → QuestionGenerator (RAG + Groq)
      ├── ask_question   → emit question to UI
      ├── evaluate       → Evaluator (Gemini/Groq)
      ├── followup       → QuestionGenerator.generate_followup
      ├── give_feedback  → scores + tips to UI
      └── wrap_up        → SessionAssessment (Gemini)
            ↓
      Knowledge Base (ChromaDB + sentence-transformers)
      ↑
  questions_seed.json (expand this to improve quality)
```

**LLM routing:**
- **Groq** (`openai/gpt-oss-120b`) → conversational turns, follow-up generation
- **Gemini** (`gemini-2.5-flash`) → deep evaluation, resume parsing, session synthesis

Override either with `GROQ_MODEL` / `GEMINI_MODEL` in `.env`.

---

## Extending the Knowledge Base

Add more entries to [`knowledge_base/questions_seed.json`](knowledge_base/questions_seed.json) following the schema:

```json
{
  "id": "unique_id",
  "category": "Technical|Behavioral|HR",
  "role": "Role Name",
  "difficulty": "Easy|Medium|Hard",
  "level": ["Fresher", "Junior", "Mid-level", "Senior", "Lead"],
  "question": "...",
  "model_answer": "...",
  "tips": ["tip1", "tip2", "tip3"],
  "tags": ["tag1", "tag2"]
}
```

Then re-run `python knowledge_base/rag_store.py` to rebuild the index.

---

## Environment Variables

| Variable | Description | Where to get |
|----------|-------------|--------------|
| `GROQ_API_KEY` | Groq LLM API key | [console.groq.com](https://console.groq.com) |
| `GOOGLE_API_KEY` | Google Gemini API key | [aistudio.google.com](https://aistudio.google.com) |

Both are **free** with generous limits.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| LLMs | Groq (`openai/gpt-oss-120b`) + Gemini (`gemini-2.5-flash`) |
| Orchestration | LangGraph + LangChain |
| Vector Store | ChromaDB (local persistent) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| UI | Flask (default) + optional Streamlit |
| Resume Parsing | pypdf + python-docx + Gemini |
| Config | python-dotenv |
