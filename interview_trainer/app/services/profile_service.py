"""
profile_service.py — Build and validate the user profile dict.
"""
from typing import Optional


def build_profile(
    name: str,
    role: str,
    level: str,
    focus: Optional[str] = None,
    difficulty: Optional[str] = None,
    resume_profile: Optional[dict] = None,
) -> dict:
    """
    Assemble a plain dict profile that will live in Flask session.
    resume_profile is the already-parsed resume dict (from resume_service).
    """
    resume_summary = None
    if resume_profile:
        resume_summary = resume_profile.get("summary", "")
        skills = resume_profile.get("skills", [])
        if skills:
            resume_summary += f" Key skills: {', '.join(skills[:5])}."

    return {
        "name": name,
        "role": role,
        "level": level,
        "focus": focus if focus and focus != "All" else None,
        "difficulty": difficulty if difficulty and difficulty != "Mixed" else None,
        "resume_summary": resume_summary,
    }
