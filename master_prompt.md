# Master Prompt – Interview Trainer Agent (RAG-Powered)

## Project Overview

**Name:** Interview Trainer Agent  
**Codename / Working Title:** PrepPilot / InterviewForge / CareerCoach-RAG  

**One-line description:**  
An intelligent, RAG-powered interview preparation agent that generates highly personalized question sets, model answers, improvement tips, and realistic mock interview sessions based on a user’s profile, experience level, target job role, and (optionally) resume.

This project is designed for the IBM Bob 2.0 Hackathon spirit: solve a real developer / professional pain point (interview anxiety + lack of targeted practice) with a working, agentic, RAG-based prototype that demonstrably improves outcomes.

---

## Expanded Problem Statement

Job seekers (especially students, early-career professionals, and career switchers) face three major problems:

1. **Generic practice material** – Most free resources give the same list of “Top 50 Interview Questions” regardless of role, seniority, or company type.
2. **No realistic feedback loop** – Users practice alone and have no idea if their answers are strong, structured, or aligned with what recruiters actually want.
3. **Fragmented preparation** – Technical questions, behavioral (STAR) stories, system design, culture-fit, and salary negotiation are usually practiced in isolation.

**Current state of the art is insufficient:**
- Generic ChatGPT prompts produce hallucinated or outdated questions.
- Existing platforms are either paid, limited in personalization, or lack true retrieval from real interview data sources.
- Most tools do not adapt difficulty, question style, or feedback based on experience level (Fresher / Mid / Senior) or specific job role.

**Solution – Interview Trainer Agent:**  
A Retrieval-Augmented Generation system that:

- Ingests and retrieves from curated sources of real interview questions, company-specific patterns, behavioral frameworks, and industry expectations.
- Accepts user profile (name, experience level, target role, optional resume upload).
- Generates **tailored** technical + behavioral + HR question sets.
- Provides model answers + improvement tips.
- Supports interactive mock interviews with follow-up questions.
- Gives structured feedback and progress tracking.

The agent acts as a patient, expert interview coach available 24/7.

---

## Core Value Proposition

- Dramatically increases interview confidence and success rate.
- Saves users dozens of hours of scattered research.
- Makes high-quality, role-specific preparation accessible for free.
- Demonstrates practical, production-style RAG + agent patterns.

---

## Expanded Feature Set (High-Impact, Implementable Features)

### Tier 1 – Must-Have (Core MVP)
1. **Profile & Role Input**
   - Name, Experience Level (Fresher / Junior / Mid / Senior / Lead), Target Job Role / Title, Optional Company type (Startup / MNC / Product / Service).
   - Optional resume upload (PDF/DOCX) → automatic extraction of skills, projects, experience.

2. **RAG-Powered Question Generation**
   - Retrieve role-specific technical questions, behavioral scenarios, and HR questions from a knowledge base.
   - Generate 8–15 personalized questions mixed by category (Technical / Behavioral / Situational / Culture-fit).

3. **Model Answers + Improvement Tips**
   - For every question, provide a strong model answer + 2–3 concrete tips to improve the user’s version.

4. **Interactive Mock Interview Mode**
   - User answers questions one-by-one (text).
   - Agent asks intelligent follow-ups based on the answer.
   - At the end, generates a performance summary.

### Tier 2 – High-Impact Medium Features (Strongly Recommended)
5. **Answer Evaluation & Scoring**
   - Score each answer on Relevance, Structure (STAR), Depth, Clarity, and Confidence indicators.
   - Give a overall readiness score (0–100) with breakdown.

6. **STAR Method Coach**
   - Specifically coach behavioral answers using Situation-Task-Action-Result framework.
   - Highlight missing parts and suggest better phrasing.

7. **Resume-to-Questions Bridge**
   - Extract key projects/skills from resume and generate “Tell me about this project” + deep-dive questions.

8. **Difficulty & Focus Controls**
   - User can choose: Easy / Medium / Hard, or focus only on System Design / Coding / Behavioral / Leadership.

9. **Progress Tracker & Weak Area Detection**
   - Store session history (local or simple DB).
   - Identify recurring weak areas and recommend focused practice sets.

10. **Company / Role Insight Cards**
    - Short “What this role usually asks” + “Common red flags” + “What good answers look like” retrieved via RAG.

### Tier 3 – Nice-to-Have / Differentiator Features (Small effort, big perceived value)
11. **Exportable Prep Report** (PDF or Markdown) – questions + model answers + personal tips.
12. **Quick Practice Modes**: “5-minute rapid fire”, “Behavioral only”, “Technical deep dive”.
13. **Confidence Builder Mode** – starts with easier questions and gradually increases difficulty.
14. **Salary Negotiation & Closing Questions** module.
15. **Multi-turn Conversation Memory** within a session so the agent remembers previous answers.

---

## Project Architecture & Plan (What the Project Should Consist Of)

### 1. Knowledge Base / RAG Layer
- Curated dataset of interview questions, behavioral scenarios, role expectations, STAR examples, and industry guidelines.
- Sources can include: public interview question banks, Glassdoor-style patterns (ethically scraped or manually curated), official company career pages summaries, common frameworks (STAR, SOAR, etc.).
- Vector store for semantic retrieval.
- Chunking strategy optimized for Q&A pairs and scenario descriptions.

### 2. Agent / Orchestration Layer
- Main Interview Coach Agent.
- Sub-agents or specialized tools:
  - Question Generator
  - Answer Evaluator / Scorer
  - STAR Coach
  - Resume Parser & Analyzer
  - Feedback Synthesizer

### 3. User Interface
- Clean, modern chat + form interface.
- Profile setup screen.
- Question list view + interactive answering mode.
- Results / feedback dashboard.

### 4. Session & Memory Management
- Short-term conversation memory for mock interviews.
- Optional long-term progress tracking.

### 5. Evaluation & Feedback Loop
- Structured scoring rubric.
- Actionable, encouraging, specific feedback (never generic).

### 6. Export & Sharing
- Ability to download a personalized preparation plan.

---

## Success Criteria (What “Done” Looks Like)

- User can input profile + optional resume → receive a high-quality, personalized question set within seconds.
- Mock interview mode feels realistic (follow-up questions make sense).
- Feedback is specific, constructive, and tied to the user’s actual answers.
- The system clearly demonstrates RAG (retrieved context is visible or cited in responses).
- Entire stack runs on free tiers (Gemini + Groq + free vector DB / local options).
- Code is clean, modular, and well-documented so IBM Bob (or any developer) can understand and extend it.

---

## Recommended Implementation Phases

**Phase 1 – Foundation (MVP)**
- Profile input + basic RAG question generation + model answers.

**Phase 2 – Interactivity**
- Mock interview mode + follow-ups + basic scoring.

**Phase 3 – Intelligence**
- Resume parsing, STAR coaching, weak-area detection, progress tracking.

**Phase 4 – Polish**
- Better UI, export report, confidence mode, company insights.

---

## Guiding Principles for the Build

- **Personalization first** – every output should feel tailored.
- **Actionable feedback** over vague praise.
- **Transparency** – show when information comes from the knowledge base.
- **Encouraging tone** – the agent is a supportive coach, not a harsh interviewer.
- **Zero cost** – stay within free API tiers and open-source components.
- **Modular & agentic** – use clear tool/agent separation so Bob can help extend features easily.

This master document defines *what* to build and *why*.  
Use the companion files (`rule.md`, `skill.md`, and technology stack) for *how* the agent should behave and the exact technical constraints.