"""
evaluation_service.py — Wraps the existing evaluator for Flask.
All return values are plain JSON-serialisable dicts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.evaluator import (
    evaluate_answer as _evaluate,
    generate_session_assessment as _session_assessment,
    AnswerScore,
)


def _score_to_dict(score: AnswerScore) -> dict:
    return {
        "relevance": score.relevance,
        "structure_clarity": score.structure_clarity,
        "depth_accuracy": score.depth_accuracy,
        "star_usage": score.star_usage,
        "confidence_indicators": score.confidence_indicators,
        "overall": score.overall,
        "strengths": score.strengths,
        "improvements": score.improvements,
        "model_tip": score.model_tip,
        "star_breakdown": score.star_breakdown,
        "improved_answer_snippet": score.improved_answer_snippet,
    }


def evaluate_answer(question: dict, answer_text: str, profile: dict) -> dict:
    """
    Evaluate a single answer. Returns a plain dict score.
    """
    score = _evaluate(
        question=question["question"],
        user_answer=answer_text,
        model_answer=question.get("model_answer", ""),
        category=question.get("category", "Technical"),
        level=profile["level"],
        role=profile["role"],
    )
    return _score_to_dict(score)


def build_session_assessment(profile: dict, qa_pairs: list[dict]) -> dict:
    """
    Synthesise a full session assessment from all Q&A pairs.
    qa_pairs: [{question, answer, score: dict, category}]
    """
    # Reconstruct AnswerScore objects for the existing function
    from tools.evaluator import AnswerScore

    reconstructed = []
    for pair in qa_pairs:
        s = pair.get("score", {})
        try:
            score_obj = AnswerScore(**s)
        except Exception:
            continue
        reconstructed.append({
            "question": pair.get("question", ""),
            "answer": pair.get("answer", ""),
            "score": score_obj,
        })

    return _session_assessment(
        qa_pairs=reconstructed,
        name=profile["name"],
        role=profile["role"],
        level=profile["level"],
    )


def generate_markdown_report(profile: dict, assessment: dict, qa_pairs: list) -> str:
    lines = [
        "# Interview Preparation Report",
        f"**Name:** {profile.get('name', '')}  ",
        f"**Role:** {profile.get('level', '')} {profile.get('role', '')}  ",
        f"**Readiness Score:** {assessment.get('readiness_score', 0)}/100\n",
        f"## Summary\n{assessment.get('summary', '')}\n",
        "## Strengths\n" + "\n".join(f"- {s}" for s in assessment.get("strengths", [])) + "\n",
        "## Priority Improvements\n" + "\n".join(f"- {w}" for w in assessment.get("weak_areas", [])) + "\n",
        "## Next Steps\n" + "\n".join(f"- {n}" for n in assessment.get("next_steps", [])) + "\n",
        "---\n## Question & Answer Review\n",
    ]
    for i, pair in enumerate(qa_pairs):
        s = pair.get("score", {})
        lines.append(f"### Q{i+1}: {pair.get('question', '')}")
        lines.append(f"**Your Answer:** {pair.get('answer', '')}\n")
        lines.append(f"**Score:** {s.get('overall', 0)}/100")
        lines.append(f"**Strengths:** {' | '.join(s.get('strengths', []))}")
        lines.append(f"**Improve:** {' | '.join(s.get('improvements', []))}")
        lines.append(f"**Tip:** {s.get('model_tip', '')}\n")
    return "\n".join(lines)
