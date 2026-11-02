"""
interview_service.py — Manages the mock interview state machine for Flask.
State is a plain dict stored in Flask session (no LangGraph runtime in session,
just the data). LangGraph / LLM calls happen per-request.
"""
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.question_generator import generate_followup_questions
from app.services.evaluation_service import evaluate_answer


def init_interview_state(profile: dict, questions: list[dict]) -> dict:
    """Create the initial interview state dict."""
    return {
        "current_index": 0,
        "followup_count": 0,
        "max_followups": 1,
        "last_question": questions[0] if questions else {},
        "awaiting_followup": False,
        "pending_followup_q": None,
    }


def process_answer(
    state: dict,
    answer_text: str,
    profile: dict,
    questions: list[dict],
    qa_pairs: list[dict],
) -> dict:
    """
    Process a user answer:
      1. Evaluate the answer.
      2. Decide whether to ask a follow-up or advance.
      3. Return updated state + qa_pairs + a response dict for the frontend.

    Returns:
        {
          "state": updated state dict,
          "qa_pairs": updated qa_pairs list,
          "response": {
              "feedback": {...},        # score dict
              "followup": str|None,     # follow-up question text, or None
              "next_question": {...}|None,
              "is_done": bool,
              "current_index": int,
              "total": int,
          }
        }
    """
    idx = state["current_index"]
    total = len(questions)

    # Which question are we evaluating?
    if state.get("awaiting_followup") and state.get("pending_followup_q"):
        # The answer is a follow-up response — evaluate against original question
        current_q = questions[idx]
    else:
        current_q = questions[idx]

    # Evaluate
    score = evaluate_answer(
        question=current_q,
        answer_text=answer_text,
        profile=profile,
    )

    # Record Q&A pair (overwrite if follow-up to same question)
    if state.get("awaiting_followup"):
        # Append as a separate follow-up pair
        qa_pairs.append({
            "question": state.get("pending_followup_q", current_q["question"]),
            "answer": answer_text,
            "score": score,
            "category": current_q.get("category", "Technical"),
            "is_followup": True,
            "original_question": current_q["question"],
        })
    else:
        qa_pairs.append({
            "question": current_q["question"],
            "answer": answer_text,
            "score": score,
            "category": current_q.get("category", "Technical"),
            "is_followup": False,
        })

    # Should we ask a follow-up?
    should_followup = (
        not state.get("awaiting_followup")           # Don't nest follow-ups
        and state["followup_count"] < state["max_followups"]
        and score["overall"] < 80
        and len(answer_text.split()) > 10
    )

    followup_q: Optional[str] = None
    if should_followup:
        try:
            followups = generate_followup_questions(
                original_question=current_q["question"],
                user_answer=answer_text,
                role=profile["role"],
                level=profile["level"],
                n=1,
            )
            followup_q = followups[0] if followups else None
        except Exception:
            followup_q = None

    # Update state
    if followup_q:
        state["awaiting_followup"] = True
        state["pending_followup_q"] = followup_q
        state["followup_count"] = state["followup_count"] + 1
        next_q = None
        is_done = False
    else:
        # Advance to next question
        state["awaiting_followup"] = False
        state["pending_followup_q"] = None
        state["followup_count"] = 0
        state["current_index"] = idx + 1
        next_idx = state["current_index"]
        is_done = next_idx >= total
        next_q = questions[next_idx] if not is_done else None
        if next_q:
            state["last_question"] = next_q

    return {
        "state": state,
        "qa_pairs": qa_pairs,
        "response": {
            "feedback": score,
            "followup": followup_q,
            "next_question": next_q,
            "is_done": is_done,
            "current_index": state["current_index"],
            "total": total,
        },
    }
