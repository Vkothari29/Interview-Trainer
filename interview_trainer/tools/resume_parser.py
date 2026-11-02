"""
Resume Parser Tool — extracts structured information from PDF or DOCX resumes.
Uses Gemini for deep understanding and structured extraction.
"""

import io
import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")


class ResumeProfile(BaseModel):
    name: Optional[str] = None
    years_of_experience: Optional[float] = None
    current_or_last_title: Optional[str] = None
    skills: list[str] = []
    programming_languages: list[str] = []
    frameworks: list[str] = []
    notable_projects: list[dict] = []   # [{"name": ..., "description": ...}]
    education: list[str] = []
    previous_roles: list[str] = []
    summary: str = ""


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def _extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[DOCX extraction error: {e}]"


def extract_text_from_resume(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a resume file (PDF or DOCX)."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _extract_text_from_docx(file_bytes)
    else:
        # Assume plain text
        return file_bytes.decode("utf-8", errors="ignore")


def parse_resume_with_llm(resume_text: str) -> ResumeProfile:
    """
    Use Google Gemini to extract structured profile data from raw resume text.
    Falls back to a minimal profile if the API key is unavailable.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        return _parse_resume_heuristic(resume_text)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            google_api_key=api_key,
            temperature=0.1,
        )

        system = (
            "You are a precise resume parser. Extract structured information from the resume text "
            "and return ONLY a valid JSON object with these exact keys: "
            "name, years_of_experience (number), current_or_last_title, skills (list), "
            "programming_languages (list), frameworks (list), "
            "notable_projects (list of {name, description}), education (list of strings), "
            "previous_roles (list of strings), summary (2-sentence summary of the candidate). "
            "Return ONLY the JSON, no explanation, no markdown fences."
        )
        user_msg = f"Resume text:\n\n{resume_text[:6000]}"

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
        raw = response.content.strip()

        # Strip markdown fences if model wraps them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return ResumeProfile(**data)

    except Exception as e:
        print(f"[ResumeParser] Gemini extraction failed ({e}), falling back to heuristic.")
        return _parse_resume_heuristic(resume_text)


def _parse_resume_heuristic(resume_text: str) -> ResumeProfile:
    """Simple keyword-based fallback parser."""
    import re

    text_lower = resume_text.lower()

    # Detect programming languages
    lang_keywords = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "kotlin", "swift", "ruby", "php", "scala", "r", "sql",
    ]
    languages = [lang for lang in lang_keywords if lang in text_lower]

    # Detect frameworks
    framework_keywords = [
        "react", "angular", "vue", "django", "flask", "fastapi", "spring", "node.js",
        "express", "nextjs", "laravel", "rails", "tensorflow", "pytorch", "langchain",
    ]
    frameworks = [fw for fw in framework_keywords if fw in text_lower]

    # Detect skills
    skill_keywords = [
        "machine learning", "deep learning", "nlp", "computer vision", "docker",
        "kubernetes", "aws", "gcp", "azure", "ci/cd", "git", "agile", "scrum",
        "microservices", "rest api", "graphql", "redis", "mongodb", "postgresql",
    ]
    skills = [sk for sk in skill_keywords if sk in text_lower]

    # Try to find a name (first non-empty line that looks like a name)
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    name = lines[0] if lines else "Unknown"

    # Rough years of experience from mentions of years
    years_match = re.findall(r"(\d+)\+?\s*years?", text_lower)
    yoe = float(max(map(int, years_match))) if years_match else None

    summary = f"Candidate with experience in {', '.join(languages[:3]) or 'software development'}."
    if frameworks:
        summary += f" Familiar with {', '.join(frameworks[:3])}."

    return ResumeProfile(
        name=name,
        years_of_experience=yoe,
        skills=skills,
        programming_languages=languages,
        frameworks=frameworks,
        summary=summary,
    )


def parse_resume(file_bytes: bytes, filename: str) -> ResumeProfile:
    """Full pipeline: extract text → parse with LLM → return ResumeProfile."""
    text = extract_text_from_resume(file_bytes, filename)
    return parse_resume_with_llm(text)
