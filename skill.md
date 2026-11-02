# Skills – Interview Trainer Agent

This document defines the concrete capabilities (skills / tools) the agent must possess.  
These skills map directly to the features described in `master_prompt.md` and are constrained by the rules in `rule.md`.

---

## Skill Categories

### 1. Profile & Context Management

**Skill: Create / Update User Profile**
- Accept and store: name, experience level, target role, preferred focus areas, optional company type.
- Accept resume upload (PDF / DOCX / text).
- Extract structured information from resume: years of experience, key skills, notable projects, education, previous roles.

**Skill: Maintain Session Context**
- Remember previous answers and feedback within a single mock interview session.
- Optionally track progress across multiple sessions (weak areas, improvement trends).

---

### 2. Knowledge Retrieval (RAG Skills)

**Skill: Retrieve Role-Specific Questions**
- Query the vector knowledge base for technical, behavioral, situational, and HR questions matching the target role + experience level.
- Support filtering by difficulty and category.

**Skill: Retrieve Model Answers & Frameworks**
- Fetch high-quality example answers, STAR templates, and explanation of what good answers look like for the given role.

**Skill: Retrieve Industry / Role Insights**
- Pull short summaries of typical expectations, common pitfalls, and evaluation criteria for the target role.

**Skill: Hybrid Search**
- Combine semantic (vector) search with keyword filtering for better precision on technical topics.

---

### 3. Question Generation & Curation

**Skill: Generate Personalized Question Set**
- Create a balanced set of 8–15 questions tailored to the user.
- Mix categories intelligently based on role (e.g., more system design for senior backend, more coding for junior, more leadership for manager roles).
- Allow user to request specific focus (e.g., “only behavioral”, “system design heavy”, “hard difficulty”).

**Skill: Generate Follow-up Questions**
- Based on a user’s answer, generate 1–3 relevant probing questions that test depth, consistency, or missing details.

---

### 4. Answer Evaluation & Coaching

**Skill: Evaluate User Answer**
- Score (or qualitatively rate) an answer on multiple dimensions.
- Identify strengths and specific weaknesses.
- Detect whether STAR structure was used effectively for behavioral questions.

**Skill: STAR Method Coaching**
- Analyze a behavioral answer against Situation / Task / Action / Result.
- Point out missing or weak components and suggest improvements.

**Skill: Generate Model Answer + Tips**
- Produce a strong sample answer.
- Explain why it works.
- Give 2–4 concrete tips the user can apply to make their own answer better.

**Skill: Overall Session Assessment**
- At the end of a mock interview, synthesize performance across all answers.
- Produce readiness score + prioritized improvement plan.

---

### 5. Interactive Modes

**Skill: Run Mock Interview Session**
- Conduct a multi-turn interview: ask → listen → follow-up → continue.
- Manage turn-taking and session state.
- Transition smoothly to feedback at the end.

**Skill: Rapid Practice / Focused Mode**
- Support short sessions (e.g., 5 questions, behavioral only, technical deep-dive).

**Skill: Confidence Builder Mode**
- Start with easier questions and progressively increase difficulty based on user performance.

---

### 6. Output & Utility Skills

**Skill: Generate Preparation Report**
- Compile questions, model answers, personal tips, and weak areas into a clean Markdown or PDF-ready report.

**Skill: Progress Summary**
- Summarize improvement over multiple sessions (if history exists).
- Highlight recurring weak areas and recommended focus.

**Skill: Explain Reasoning (Transparency)**
- When useful, briefly indicate that certain questions or advice came from the knowledge base / common patterns for the role.

---

## Skill Implementation Guidelines

- Each major skill should be implemented as a clear, callable tool or sub-agent so the main coach agent can orchestrate them.
- Prefer structured outputs (JSON where appropriate) for evaluation scores and extracted resume data so downstream logic remains reliable.
- Always ground generation in retrieved context when possible (true RAG behavior).
- Keep latency reasonable — prioritize fast models (Groq) for interactive turns and stronger models (Gemini) for deeper evaluation / report generation when needed.

---

## Priority Order for Implementation

1. Profile handling + Resume extraction  
2. RAG question retrieval + personalized question set generation  
3. Model answers + tips  
4. Basic answer evaluation  
5. Full mock interview loop with follow-ups  
6. STAR coaching  
7. Session assessment + progress tracking  
8. Report generation  

Mastering the first five skills already delivers a highly valuable product.