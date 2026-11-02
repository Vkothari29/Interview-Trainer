"""
Question Generator Tool — produces a personalized question set for the user.
Combines RAG retrieval with Groq LLM to fill gaps and personalize questions.
"""

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent to path for cross-module imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base.rag_store import retrieve_all_for_role, retrieve_questions


def _get_groq_llm(temperature: float = 0.4):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("your_"):
        return None
    from langchain_groq import ChatGroq
    return ChatGroq(
        # llama-3.3-70b-versatile is now an Enterprise-only model on Groq.
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        groq_api_key=api_key,
        temperature=temperature,
    )


def _get_gemini_llm(temperature: float = 0.3):
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        # gemini-1.5-flash was retired; allow overriding via env.
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=temperature,
    )


def generate_question_set(
    name: str,
    role: str,
    level: str,
    focus: Optional[str] = None,          # "behavioral", "technical", "system design", etc.
    difficulty: Optional[str] = None,      # "Easy", "Medium", "Hard"
    resume_summary: Optional[str] = None,
    n_questions: int = 10,
) -> list[dict]:
    """
    Generate a personalized interview question set.
    Returns a list of question dicts: {question, category, difficulty, model_answer, tips, source}.
    """
    # 1. Retrieve relevant questions from RAG
    query = f"{level} {role} interview questions"
    if focus:
        query += f" focusing on {focus}"
    if resume_summary:
        query += f". Candidate background: {resume_summary[:200]}"

    rag_questions = retrieve_all_for_role(role=role, level=level, n_results=n_questions + 4)

    # Filter by focus category if specified
    category_map = {
        "behavioral": "Behavioral",
        "technical": "Technical",
        "hr": "HR",
        "system design": "Technical",
    }
    if focus and focus.lower() in category_map:
        cat_filter = category_map[focus.lower()]
        rag_questions = [q for q in rag_questions if q["category"] == cat_filter] or rag_questions

    # Filter by difficulty if specified
    if difficulty:
        diff_filtered = [q for q in rag_questions if q["difficulty"] == difficulty]
        rag_questions = diff_filtered if diff_filtered else rag_questions

    # Mark source
    for q in rag_questions:
        q["source"] = "knowledge_base"

    # 2. If we have fewer than requested, supplement with LLM-generated questions
    if len(rag_questions) < n_questions:
        gap = n_questions - len(rag_questions)
        llm_questions = _generate_llm_questions(
            name=name,
            role=role,
            level=level,
            focus=focus,
            resume_summary=resume_summary,
            existing_questions=[q["question"] for q in rag_questions],
            n=gap,
        )
        rag_questions.extend(llm_questions)

    # Balance the full pool first, then take the requested number.
    # (Slicing first can leave an all-Technical or all-HR set.)
    balanced = _balance_question_set(rag_questions)
    if not balanced:
        balanced = _fallback_question_set(role=role, level=level, n=n_questions)
    return balanced[:n_questions]


def _fallback_question_set(role: str, level: str, n: int = 10) -> list[dict]:
    """Last-resort question set so the app never returns an empty interview."""
    base = [
        {
            "question": f"Walk me through your background and why you're a good fit for this {level} {role} role.",
            "category": "HR",
            "difficulty": "Easy",
            "model_answer": "Summarize your relevant experience, highlight two or three concrete achievements, and connect them to the role's requirements.",
            "tips": ["Keep it under two minutes", "End with why you want this specific role"],
        },
        {
            "question": f"What are the core technical skills a {role} needs, and which are your strongest?",
            "category": "Technical",
            "difficulty": "Medium",
            "model_answer": "Name the key skills for the role, then give evidence of depth for the ones you know best, including a project or measurable outcome.",
            "tips": ["Be specific about depth", "Use a real example"],
        },
        {
            "question": "Describe a challenging problem you solved recently. What was your approach?",
            "category": "Behavioral",
            "difficulty": "Medium",
            "model_answer": "Use STAR: describe the situation, your task, the actions you took, and the measurable result.",
            "tips": ["Quantify the result", "Explain trade-offs you considered"],
        },
        {
            "question": f"How do you stay current with changes in {role} work?",
            "category": "HR",
            "difficulty": "Easy",
            "model_answer": "Mention specific sources you follow, courses or certifications, and a recent thing you learned and applied.",
            "tips": ["Name concrete resources", "Show application, not just consumption"],
        },
        {
            "question": "Tell me about a time you disagreed with a teammate. How did you resolve it?",
            "category": "Behavioral",
            "difficulty": "Medium",
            "model_answer": "Describe the disagreement neutrally, how you listened, the evidence you used, and the outcome for the team.",
            "tips": ["Focus on the resolution", "Avoid blaming others"],
        },
        {
            "question": "What is your biggest weakness, and what are you doing about it?",
            "category": "HR",
            "difficulty": "Medium",
            "model_answer": "Pick a genuine but non-fatal weakness, explain its impact, and describe the concrete steps you are taking to improve.",
            "tips": ["Be honest", "Show measurable progress"],
        },
        {
            "question": f"Explain a concept in {role} work that you find commonly misunderstood.",
            "category": "Technical",
            "difficulty": "Hard",
            "model_answer": "Define the concept clearly, explain why it is misunderstood, and give an example of the practical consequences.",
            "tips": ["Use a simple analogy", "Finish with a concrete example"],
        },
        {
            "question": "Describe a time you had to prioritize competing deadlines.",
            "category": "Behavioral",
            "difficulty": "Medium",
            "model_answer": "Explain how you assessed impact and urgency, communicated trade-offs, and delivered the most important work.",
            "tips": ["Mention stakeholder communication", "State the outcome"],
        },
        {
            "question": "Why do you want to work here, and what do you know about our team?",
            "category": "HR",
            "difficulty": "Easy",
            "model_answer": "Connect the company's product, mission, or engineering culture to your own goals and experience.",
            "tips": ["Research the company beforehand", "Be specific, not generic"],
        },
        {
            "question": f"How would you design or improve a typical {role} workflow end to end?",
            "category": "Technical",
            "difficulty": "Hard",
            "model_answer": "Break the workflow into stages, identify bottlenecks and failure modes, propose improvements, and explain how you would measure success.",
            "tips": ["Discuss trade-offs", "Define success metrics"],
        },
    ]
    return base[:n]


def _balance_question_set(questions: list[dict]) -> list[dict]:
    """Ensure a reasonable mix of Technical / Behavioral / HR questions."""
    if not questions:
        return questions
    tech = [q for q in questions if q.get("category") == "Technical"]
    behav = [q for q in questions if q.get("category") == "Behavioral"]
    hr = [q for q in questions if q.get("category") == "HR"]
    other = [q for q in questions if q.get("category") not in ("Technical", "Behavioral", "HR")]

    balanced = []
    # Aim for ~50% tech, 30% behavioral, 20% HR
    target_tech = max(1, int(len(questions) * 0.5))
    target_behav = max(1, int(len(questions) * 0.3))
    target_hr = len(questions) - target_tech - target_behav

    balanced.extend(tech[:target_tech])
    balanced.extend(behav[:target_behav])
    balanced.extend(hr[:target_hr])
    balanced.extend(other)

    # Pad with whatever is left if short
    remaining = [q for q in questions if q not in balanced]
    balanced.extend(remaining[: len(questions) - len(balanced)])
    return balanced[: len(questions)]


def _generate_llm_questions(
    name: str,
    role: str,
    level: str,
    focus: Optional[str],
    resume_summary: Optional[str],
    existing_questions: list[str],
    n: int,
) -> list[dict]:
    """Generate additional questions via Groq LLM when RAG doesn't have enough."""
    llm = _get_groq_llm() or _get_gemini_llm()
    if not llm or n <= 0:
        return []

    from langchain_core.messages import HumanMessage, SystemMessage

    existing_str = "\n".join(f"- {q}" for q in existing_questions[:10])
    resume_str = f"\nCandidate background: {resume_summary}" if resume_summary else ""
    focus_str = f"\nFocus area: {focus}" if focus else ""

    system = (
        "You are an expert technical interviewer. Generate interview questions as a JSON array. "
        "Each object must have: question (string), category (Technical|Behavioral|HR), "
        "difficulty (Easy|Medium|Hard), model_answer (string, 3-5 sentences), "
        "tips (array of 2-3 strings). Return ONLY the JSON array, no markdown, no explanation."
    )
    user_msg = (
        f"Generate {n} interview questions for a {level} {role}.{focus_str}{resume_str}\n"
        f"Do NOT repeat these already-selected questions:\n{existing_str}"
    )

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        items = json.loads(raw)
        for item in items:
            item["source"] = "llm_generated"
            item.setdefault("tags", [])
        return items
    except Exception as e:
        print(f"[QuestionGenerator] LLM generation failed: {e}")
        return []


def generate_followup_questions(
    original_question: str,
    user_answer: str,
    role: str,
    level: str,
    n: int = 2,
) -> list[str]:
    """
    Generate intelligent follow-up questions based on the user's answer.
    Uses Groq for speed.
    """
    llm = _get_groq_llm(temperature=0.5) or _get_gemini_llm(temperature=0.5)
    if not llm:
        return [
            "Can you walk me through a specific example of that?",
            "What was the biggest challenge you faced in that situation?",
        ]

    from langchain_core.messages import HumanMessage, SystemMessage

    system = (
        "You are a senior technical interviewer. Based on the original question and candidate's answer, "
        f"generate {n} intelligent follow-up questions that probe deeper, test consistency, or "
        "explore missing details. Return ONLY a JSON array of question strings."
    )
    user_msg = (
        f"Original question: {original_question}\n\n"
        f"Candidate's answer: {user_answer}\n\n"
        f"Generate {n} follow-up questions for a {level} {role}."
    )

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        questions = json.loads(raw)
        return questions[:n] if isinstance(questions, list) else []
    except Exception as e:
        print(f"[QuestionGenerator] Follow-up generation failed: {e}")
        return ["Can you give me a concrete example?", "What would you do differently now?"]
