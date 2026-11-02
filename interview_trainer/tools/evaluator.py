"""
Answer Evaluator & STAR Coach Tool.
Scores user answers across multiple dimensions and provides constructive feedback.
Uses Gemini for deep evaluation quality; falls back to Groq if unavailable.
"""

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")


class AnswerScore(BaseModel):
    relevance: int           # 0-10
    structure_clarity: int   # 0-10
    depth_accuracy: int      # 0-10
    star_usage: int          # 0-10 (10 if not behavioral)
    confidence_indicators: int  # 0-10
    overall: int             # 0-100

    strengths: list[str]
    improvements: list[str]
    model_tip: str
    star_breakdown: Optional[dict] = None  # {situation, task, action, result} scores
    improved_answer_snippet: str = ""


def _get_evaluation_llm():
    """Prefer Gemini for evaluations (better reasoning), fall back to Groq."""
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if gemini_key and not gemini_key.startswith("your_"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                # gemini-1.5-flash was retired; allow overriding via env.
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                google_api_key=gemini_key,
                temperature=0.2,
            )
        except Exception:
            pass

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("your_"):
        from langchain_groq import ChatGroq
        return ChatGroq(
            # llama-3.3-70b-versatile is now an Enterprise-only model on Groq.
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            groq_api_key=groq_key,
            temperature=0.2,
        )
    return None


def evaluate_answer(
    question: str,
    user_answer: str,
    model_answer: str,
    category: str,  # "Technical", "Behavioral", "HR"
    level: str,
    role: str,
) -> AnswerScore:
    """
    Evaluate a user's answer against the question and a model answer.
    Returns a structured AnswerScore with scores and qualitative feedback.
    """
    llm = _get_evaluation_llm()
    if not llm:
        return _fallback_evaluation(user_answer, category)

    from langchain_core.messages import HumanMessage, SystemMessage

    is_behavioral = category == "Behavioral"
    star_instruction = (
        "Also evaluate STAR usage: separately score Situation (0-10), Task (0-10), "
        "Action (0-10), Result (0-10) and include as 'star_breakdown' object."
        if is_behavioral else
        "Set 'star_usage' to 10 and 'star_breakdown' to null (not a behavioral question)."
    )

    system = f"""You are a senior technical interviewer evaluating a candidate's answer.
Score the answer on these dimensions (each 0–10):
- relevance: How directly does the answer address the question?
- structure_clarity: Is the answer well-organized and easy to follow?
- depth_accuracy: Is the answer technically accurate and sufficiently deep for a {level} {role}?
- star_usage: For behavioral questions, was STAR used effectively?
- confidence_indicators: Does the answer show confidence and ownership?

Also compute 'overall' as a 0–100 score (weighted average).

{star_instruction}

Provide:
- strengths: list of 2-3 specific strengths (strings)
- improvements: list of 2-3 specific, actionable improvements (strings)
- model_tip: One concise tip to make the answer significantly stronger (1-2 sentences)
- improved_answer_snippet: A 2-3 sentence rewrite of the weakest part of their answer

Return ONLY a valid JSON object with exactly these keys:
relevance, structure_clarity, depth_accuracy, star_usage, confidence_indicators,
overall, strengths, improvements, model_tip, star_breakdown, improved_answer_snippet
No markdown, no explanation."""

    user_msg = f"""Question: {question}

Model Answer (for reference): {model_answer}

Candidate's Answer: {user_answer}

Experience level: {level} {role}"""

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return AnswerScore(**data)
    except Exception as e:
        print(f"[Evaluator] LLM evaluation failed ({e}), using fallback.")
        return _fallback_evaluation(user_answer, category)


def coach_star_answer(
    question: str,
    user_answer: str,
) -> dict:
    """
    Provide detailed STAR framework coaching for a behavioral answer.
    Returns a dict with identified S/T/A/R parts, gaps, and an improved outline.
    """
    llm = _get_evaluation_llm()
    if not llm:
        return {
            "identified": {"situation": "", "task": "", "action": "", "result": ""},
            "missing": ["Could not identify — please add an API key for detailed coaching."],
            "improved_outline": "",
        }

    from langchain_core.messages import HumanMessage, SystemMessage

    system = """You are a STAR method interview coach.
Analyze the candidate's behavioral answer and return a JSON object with:
- identified: {situation: "...", task: "...", action: "...", result: "..."} — what they said for each component (empty string if missing)
- missing: list of which STAR components are weak or absent
- score_per_component: {situation: 0-10, task: 0-10, action: 0-10, result: 0-10}
- improved_outline: A bullet-point outline showing how to restructure the answer using STAR (3-5 bullets)
- key_advice: One sentence of the most important STAR advice for this specific answer

Return ONLY valid JSON, no markdown, no explanation."""

    user_msg = f"Question: {question}\n\nCandidate's Answer: {user_answer}"

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"[STARCoach] Failed: {e}")
        return {
            "identified": {"situation": "", "task": "", "action": "", "result": ""},
            "missing": ["Unable to analyze — check your API keys."],
            "improved_outline": "",
        }


def generate_session_assessment(
    qa_pairs: list[dict],  # [{question, answer, score: AnswerScore}]
    name: str,
    role: str,
    level: str,
) -> dict:
    """
    Synthesize a full session assessment from all Q&A pairs.
    Returns readiness score, strengths, weak areas, and next steps.
    """
    if not qa_pairs:
        return {"readiness_score": 0, "summary": "No answers to assess.", "strengths": [], "weak_areas": [], "next_steps": []}

    # Compute average overall score
    scores = [pair["score"].overall for pair in qa_pairs if pair.get("score")]
    avg_score = int(sum(scores) / len(scores)) if scores else 0

    # Aggregate strengths and improvements
    all_strengths = []
    all_improvements = []
    for pair in qa_pairs:
        score = pair.get("score")
        if score:
            all_strengths.extend(score.strengths)
            all_improvements.extend(score.improvements)

    llm = _get_evaluation_llm()
    if not llm:
        return {
            "readiness_score": avg_score,
            "summary": f"{name} completed the mock interview session.",
            "strengths": list(set(all_strengths))[:3],
            "weak_areas": list(set(all_improvements))[:3],
            "next_steps": ["Practice behavioral questions using STAR.", "Review system design fundamentals."],
        }

    from langchain_core.messages import HumanMessage, SystemMessage

    qa_summary = "\n\n".join(
        f"Q: {p['question']}\nScore: {p['score'].overall}/100\n"
        f"Strengths: {', '.join(p['score'].strengths[:2])}\n"
        f"Improvements: {', '.join(p['score'].improvements[:2])}"
        for p in qa_pairs if p.get("score")
    )

    system = """You are a senior interview coach synthesizing a mock interview session.
Return a JSON object with:
- readiness_score: 0-100 integer
- summary: 2-3 sentence overall assessment (encouraging and honest)
- strengths: list of 3 top demonstrated strengths
- weak_areas: list of 3 priority areas to improve (specific, actionable)
- next_steps: list of 3 concrete recommended practice activities
Return ONLY valid JSON."""

    user_msg = (
        f"Candidate: {name} | Role: {level} {role}\n"
        f"Average score: {avg_score}/100\n\n"
        f"Session Q&A summary:\n{qa_summary}"
    )

    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        result["readiness_score"] = avg_score  # Use computed average, not LLM's guess
        return result
    except Exception as e:
        print(f"[SessionAssessment] Failed: {e}")
        return {
            "readiness_score": avg_score,
            "summary": f"{name} completed {len(qa_pairs)} questions with an average score of {avg_score}/100.",
            "strengths": list(set(all_strengths))[:3],
            "weak_areas": list(set(all_improvements))[:3],
            "next_steps": ["Review and practice weak areas.", "Re-run mock interview in 2 days."],
        }


def _fallback_evaluation(user_answer: str, category: str) -> AnswerScore:
    """Minimal evaluation when no LLM is available."""
    word_count = len(user_answer.split())
    base = min(50 + word_count // 5, 70)
    return AnswerScore(
        relevance=7,
        structure_clarity=6,
        depth_accuracy=6,
        star_usage=10 if category != "Behavioral" else 5,
        confidence_indicators=6,
        overall=base,
        strengths=["Answer provided.", "Shows engagement with the question."],
        improvements=["Add more specific examples.", "Quantify your results where possible."],
        model_tip="Add a concrete example with measurable outcomes to make this answer memorable.",
        improved_answer_snippet="",
    )
