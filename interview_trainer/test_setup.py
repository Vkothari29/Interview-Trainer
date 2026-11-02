"""
Quick validation test -- checks all modules import correctly and core logic works
without requiring real API keys.
Run from: interview_trainer/
  py test_setup.py
"""

import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    print("Testing imports...")
    from knowledge_base.rag_store import build_vector_store, retrieve_all_for_role
    from tools.resume_parser import ResumeProfile, _parse_resume_heuristic
    from tools.question_generator import _balance_question_set
    from tools.evaluator import AnswerScore, _fallback_evaluation
    from agent.coach_agent import InterviewSession, node_start_session
    print("  [OK] All imports OK")


def test_knowledge_base():
    print("Testing knowledge base build...")
    from knowledge_base.rag_store import build_vector_store, retrieve_all_for_role
    collection = build_vector_store()
    count = collection.count()
    assert count > 0, "Collection is empty after build!"
    print(f"  [OK] Knowledge base built: {count} documents")

    results = retrieve_all_for_role("Software Engineer", "Mid-level", n_results=3)
    assert len(results) > 0, "No results returned from retrieval!"
    print(f"  [OK] RAG retrieval OK: got {len(results)} questions")
    for r in results:
        print(f"     [{r['category']}] {r['question'][:60]}...")


def test_resume_parser():
    print("Testing resume parser (heuristic fallback)...")
    from tools.resume_parser import _parse_resume_heuristic
    sample = """
    Jane Smith
    5 years of experience as a Backend Engineer.
    Skills: Python, Go, Docker, Kubernetes, PostgreSQL, Redis, AWS
    Frameworks: FastAPI, Django
    Education: B.Sc. Computer Science, MIT
    """
    profile = _parse_resume_heuristic(sample)
    assert "python" in profile.programming_languages, "Python not detected"
    assert profile.years_of_experience == 5.0, f"YoE wrong: {profile.years_of_experience}"
    print(f"  [OK] Resume parser OK: {profile.programming_languages}, {profile.years_of_experience} yrs")


def test_question_balancer():
    print("Testing question set balancer...")
    from tools.question_generator import _balance_question_set
    questions = [
        {"category": "Technical", "question": f"Tech Q{i}"} for i in range(8)
    ] + [
        {"category": "Behavioral", "question": f"Behav Q{i}"} for i in range(4)
    ] + [
        {"category": "HR", "question": f"HR Q{i}"} for i in range(2)
    ]
    balanced = _balance_question_set(questions)
    assert len(balanced) <= len(questions)
    cats = [q["category"] for q in balanced]
    assert "Technical" in cats and "Behavioral" in cats
    print(f"  [OK] Balancer OK: {len(balanced)} questions, categories: {set(cats)}")


def test_fallback_evaluator():
    print("Testing fallback evaluator...")
    from tools.evaluator import _fallback_evaluation
    score = _fallback_evaluation("I used Python to build a REST API with FastAPI.", "Technical")
    assert 0 <= score.overall <= 100
    assert len(score.strengths) > 0
    assert len(score.improvements) > 0
    print(f"  [OK] Fallback evaluator OK: overall={score.overall}")


def test_session_init():
    print("Testing InterviewSession initialization (no API keys needed for init)...")
    from agent.coach_agent import InterviewSession
    session = InterviewSession(
        name="Test User",
        role="Software Engineer",
        level="Mid-level",
    )
    assert session.state["name"] == "Test User"
    assert session.state["phase"] == "setup"
    assert session.total_questions == 0  # Not started yet
    print("  [OK] Session init OK")


if __name__ == "__main__":
    print("=" * 55)
    print("  Interview Trainer Agent - Setup Validation")
    print("=" * 55)
    all_passed = True
    tests = [
        test_imports,
        test_knowledge_base,
        test_resume_parser,
        test_question_balancer,
        test_fallback_evaluator,
        test_session_init,
    ]
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  [FAIL] FAILED: {e}")
            import traceback; traceback.print_exc()
            all_passed = False
    print("=" * 55)
    if all_passed:
        print("  [PASS] All tests passed! Run: py -m streamlit run app.py")
    else:
        print("  [FAIL] Some tests failed. See errors above.")
    print("=" * 55)
