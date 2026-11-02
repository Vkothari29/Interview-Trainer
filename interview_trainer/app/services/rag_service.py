"""
rag_service.py — Wraps the existing RAG layer for Flask use.
Returns plain dicts (no Pydantic models) so they are JSON-serialisable
and can be stored directly in Flask session.
"""
import sys
from pathlib import Path

# Ensure root is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_base.rag_store import build_vector_store, retrieve_all_for_role
from tools.question_generator import generate_question_set as _gen_qs


def _question_to_dict(q: dict) -> dict:
    """Ensure a question object is a plain serialisable dict."""
    return {
        "id": q.get("id", ""),
        "category": q.get("category", "Technical"),
        "question": q.get("question", ""),
        "model_answer": q.get("model_answer", ""),
        "tips": q.get("tips", []),
        "difficulty": q.get("difficulty", "Medium"),
        "tags": q.get("tags", []),
        "source": q.get("source", "knowledge_base"),
    }


def ensure_vector_store() -> None:
    """Build the vector store on first use (idempotent)."""
    try:
        build_vector_store()
    except Exception as e:
        print(f"[RAG] Vector store init warning: {e}")


def get_question_set(profile: dict, n: int = 10) -> list[dict]:
    """
    Generate a personalized question set for the given profile.
    Returns a list of plain dicts (session-safe).
    """
    ensure_vector_store()
    questions = _gen_qs(
        name=profile["name"],
        role=profile["role"],
        level=profile["level"],
        focus=profile.get("focus"),
        difficulty=profile.get("difficulty"),
        resume_summary=profile.get("resume_summary"),
        n_questions=n,
    )
    return [_question_to_dict(q) for q in questions]
