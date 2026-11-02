# Technology Stack – Interview Trainer Agent

**Constraint:** Completely free to build and run. No paid services, no credit card required for core functionality.  
**Required LLM providers:** Google Gemini (via Google AI Studio) + Groq.

This stack is deliberately chosen for:
- Zero cost (generous free tiers)
- Fast iteration
- Strong RAG support
- Easy agent orchestration
- Compatibility with IBM Bob-style development

---

## 1. Language & Runtime

- **Python 3.11+** (primary language)
- Recommended: Use a virtual environment (`venv` or `uv`)

---

## 2. LLM Providers (Mandatory)

| Provider       | Use Case                          | Free Tier Notes                          | Recommended Models                  |
|----------------|-----------------------------------|------------------------------------------|-------------------------------------|
| **Groq**       | Fast interactive turns, follow-ups, scoring, chat | Very high speed, generous daily limits  | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b` |
| **Google Gemini** | Deeper reasoning, resume analysis, high-quality model answers, final reports | Free tier via Google AI Studio (no credit card) | `gemini-1.5-flash`, `gemini-1.5-pro` (or latest free equivalents) |

**Strategy:**
- Use **Groq** as the default for most agent turns (speed + cost).
- Route complex tasks (resume parsing, deep evaluation, report synthesis) to **Gemini**.
- Both keys must be supported via environment variables.

---

## 3. RAG / Vector Store

**Recommended (fully free options):**

1. **ChromaDB** (local / persistent) – simplest and completely free.
2. **FAISS** (local) – excellent performance, no server needed.
3. **Qdrant** – free cloud tier available (1 GB), or self-hosted.

**Embedding models (free):**
- `sentence-transformers/all-MiniLM-L6-v2` (local, fast, good quality)
- Or Gemini / other free embedding endpoints if preferred.

**Knowledge Base Content:**
- Curated Q&A pairs, behavioral scenarios, role expectations, STAR examples.
- Start with a solid seed dataset (can be expanded later).
- Store as JSON / Markdown / simple documents and ingest into the vector store.

---

## 4. Agent / Orchestration Framework

**Primary recommendation:**
- **LangChain** + **LangGraph** (excellent for stateful mock interviews and multi-step agents)

**Strong alternatives (also free):**
- LlamaIndex (excellent for RAG-heavy workloads)
- CrewAI (if you want multi-agent role separation)
- Pure custom agents with tool calling (lighter weight)

LangGraph is particularly good for the mock interview state machine (ask → wait → evaluate → follow-up → end).

---

## 5. Document / Resume Processing

- `pypdf` or `pdfplumber` for PDF
- `python-docx` for DOCX
- Optional: `unstructured` (free community version) for more robust parsing

---

## 6. Frontend / UI

**Recommended free options (pick one):**

| Option              | Best For                     | Notes                              |
|---------------------|------------------------------|------------------------------------|
| **Streamlit**       | Fastest MVP, pure Python     | Excellent for demos and hackathons |
| **Gradio**          | Chat-style interfaces        | Very quick to build conversational UI |
| **Next.js + FastAPI** | More polished production feel | Requires a bit more setup         |
| **Chainlit**        | Agent-focused chat UI        | Good middle ground                 |

For IBM Bob / hackathon speed → **Streamlit** or **Gradio** is ideal.

---

## 7. Backend / API (if needed)

- FastAPI (if you separate frontend and backend)
- Or pure Streamlit / Gradio (no separate backend required)

---

## 8. Memory & Session Storage

- In-memory for single sessions (LangChain memory)
- SQLite or local JSON files for simple progress tracking
- Optional: free-tier Supabase / Neon / Turso if you want cloud persistence later (still free)

---

## 9. Environment & Secrets

- `.env` file with:
  - `GROQ_API_KEY=`
  - `GOOGLE_API_KEY=` (or `GEMINI_API_KEY=`)
- Use `python-dotenv`

---

## 10. Supporting Libraries (all free / open-source)

- `langchain`, `langchain-groq`, `langchain-google-genai`
- `langgraph`
- `chromadb` or `faiss-cpu`
- `sentence-transformers`
- `pydantic` (for structured outputs)
- `python-dotenv`
- `streamlit` or `gradio`
- `pypdf` / `python-docx`

---

## 11. Deployment (Free Options)

- Streamlit Community Cloud
- Hugging Face Spaces
- Render / Railway free tier
- Local only (perfectly fine for demonstration)

---

## Recommended Minimal Stack for Fastest High-Quality MVP

```
Python 3.11+
LangChain + LangGraph
Groq (primary) + Gemini (secondary)
ChromaDB (local) + sentence-transformers
Streamlit
pypdf + python-docx
```

This combination is:
- 100% free
- Fast to develop
- Strong RAG capabilities
- Excellent agent orchestration
- Easy for IBM Bob to understand and extend

---

## Architecture Sketch

```
User (Streamlit/Gradio)
        ↓
Main Coach Agent (LangGraph)
        ↓
   ┌────┼────┬─────────────┐
   ↓    ↓    ↓             ↓
Profile  RAG  Evaluator   Resume
Tool    Tool   Tool       Parser
   ↓    ↓
Chroma / FAISS  ←  Knowledge Base (questions, STAR, insights)
```

Use Groq for the main conversational loop and Gemini when higher reasoning quality is needed.

---

This stack fully satisfies the zero-cost requirement while giving you powerful RAG + agent capabilities with the exact LLM providers you requested (Gemini + Groq).