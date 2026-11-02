"""
resume_service.py — Wraps the existing resume parser for Flask.
Returns plain dicts so they are JSON/session-safe.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.resume_parser import parse_resume, ResumeProfile


def parse_resume_file(filepath: str) -> dict:
    """
    Parse a resume from disk and return a plain dict.
    """
    with open(filepath, "rb") as f:
        file_bytes = f.read()

    filename = Path(filepath).name
    profile: ResumeProfile = parse_resume(file_bytes, filename)

    return {
        "name": profile.name,
        "years_of_experience": profile.years_of_experience,
        "current_or_last_title": profile.current_or_last_title,
        "skills": profile.skills,
        "programming_languages": profile.programming_languages,
        "frameworks": profile.frameworks,
        "notable_projects": profile.notable_projects,
        "education": profile.education,
        "previous_roles": profile.previous_roles,
        "summary": profile.summary,
    }
