"""
app/routes.py — All Flask routes.
Routes are thin: validate input → call service → render template or return JSON.
"""
import os
import uuid
from pathlib import Path
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, jsonify, flash, send_file
)
from werkzeug.utils import secure_filename

main_bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────────────────────────────────────
# GET /  →  Profile form
# ──────────────────────────────────────────────
@main_bp.route("/")
def index():
    return render_template("index.html")


# ──────────────────────────────────────────────
# POST /upload-resume
# ──────────────────────────────────────────────
@main_bp.route("/upload-resume", methods=["POST"])
def upload_resume():
    from app.services.resume_service import parse_resume_file

    file = request.files.get("resume")
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No file provided"}), 400
    if not _allowed(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type"}), 400

    upload_dir = Path(
        os.environ.get("UPLOAD_FOLDER", Path(__file__).parent / "static" / "uploads")
    )
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = upload_dir / filename
    file.save(str(filepath))

    try:
        resume_profile = parse_resume_file(str(filepath))
        session["resume_profile"] = resume_profile
        return jsonify({"success": True, "summary": resume_profile.get("summary", "")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ──────────────────────────────────────────────
# POST /generate-questions
# ──────────────────────────────────────────────
@main_bp.route("/generate-questions", methods=["POST"])
def generate_questions():
    from app.services.profile_service import build_profile
    from app.services.rag_service import get_question_set

    data = request.form
    name = data.get("name", "").strip()
    role = data.get("role", "").strip()
    level = data.get("level", "Mid-level")
    focus = data.get("focus") or None
    difficulty = data.get("difficulty") or None

    if not name or not role:
        flash("Name and role are required.", "danger")
        return redirect(url_for("main.index"))

    profile = build_profile(
        name=name, role=role, level=level,
        focus=focus, difficulty=difficulty,
        resume_profile=session.get("resume_profile"),
    )
    session["profile"] = profile

    questions = get_question_set(profile)
    session["questions"] = questions
    session["qa_pairs"] = []
    # A new question set invalidates any assessment from a previous run.
    session.pop("session_assessment", None)

    return redirect(url_for("main.questions_page"))


# ──────────────────────────────────────────────
# GET /questions  →  View question set
# ──────────────────────────────────────────────
@main_bp.route("/questions")
def questions_page():
    questions = session.get("questions")
    profile = session.get("profile")
    if not questions or not profile:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("main.index"))
    return render_template("questions.html", questions=questions, profile=profile)


# ──────────────────────────────────────────────
# POST /mock-interview/start  →  Start session
# ──────────────────────────────────────────────
@main_bp.route("/mock-interview/start", methods=["POST"])
def start_mock_interview():
    from app.services.interview_service import init_interview_state

    profile = session.get("profile")
    questions = session.get("questions")
    if not profile or not questions:
        flash("Please generate questions first.", "warning")
        return redirect(url_for("main.index"))

    state = init_interview_state(profile, questions)
    session["interview_state"] = state
    session["qa_pairs"] = []
    session.pop("session_assessment", None)
    return redirect(url_for("main.mock_interview"))


# ──────────────────────────────────────────────
# GET /mock-interview  →  Live interview page
# ──────────────────────────────────────────────
@main_bp.route("/mock-interview")
def mock_interview():
    state = session.get("interview_state")
    profile = session.get("profile")
    if not state or not profile:
        flash("Start an interview first.", "warning")
        return redirect(url_for("main.index"))

    questions = session.get("questions", [])
    current_idx = state.get("current_index", 0)
    is_done = current_idx >= len(questions)

    if is_done:
        return redirect(url_for("main.results"))

    current_q = questions[current_idx]
    return render_template(
        "mock_interview.html",
        profile=profile,
        current_q=current_q,
        current_idx=current_idx,
        total=len(questions),
        qa_pairs=session.get("qa_pairs", []),
    )


# ──────────────────────────────────────────────
# POST /mock-interview/answer  →  JSON API
# ──────────────────────────────────────────────
@main_bp.route("/mock-interview/answer", methods=["POST"])
def submit_answer():
    from app.services.interview_service import process_answer

    body = request.get_json(silent=True) or {}
    answer_text = body.get("answer", "").strip()
    if not answer_text:
        return jsonify({"error": "Empty answer"}), 400

    state = session.get("interview_state")
    profile = session.get("profile")
    questions = session.get("questions", [])
    qa_pairs = session.get("qa_pairs", [])

    if not state or not profile:
        return jsonify({"error": "No active session"}), 400

    result = process_answer(
        state=state,
        answer_text=answer_text,
        profile=profile,
        questions=questions,
        qa_pairs=qa_pairs,
    )

    # Persist updated state back to session
    session["interview_state"] = result["state"]
    session["qa_pairs"] = result["qa_pairs"]
    # Scores changed, so any cached assessment is stale.
    session.pop("session_assessment", None)

    return jsonify(result["response"])


# ──────────────────────────────────────────────
# GET /results  →  Final assessment page
# ──────────────────────────────────────────────
@main_bp.route("/results")
def results():
    from app.services.evaluation_service import build_session_assessment

    profile = session.get("profile")
    qa_pairs = session.get("qa_pairs", [])

    if not profile:
        return redirect(url_for("main.index"))

    assessment = session.get("session_assessment")
    if not assessment:
        assessment = build_session_assessment(profile, qa_pairs)
        session["session_assessment"] = assessment

    return render_template("results.html", profile=profile,
                           assessment=assessment, qa_pairs=qa_pairs)


# ──────────────────────────────────────────────
# GET /feedback/<int:q_index>  →  Per-Q detail
# ──────────────────────────────────────────────
@main_bp.route("/feedback/<int:q_index>")
def feedback(q_index: int):
    qa_pairs = session.get("qa_pairs", [])
    profile = session.get("profile")
    if q_index >= len(qa_pairs):
        return redirect(url_for("main.results"))
    pair = qa_pairs[q_index]
    return render_template("feedback.html", pair=pair, index=q_index,
                           total=len(qa_pairs), profile=profile)


# ──────────────────────────────────────────────
# GET /download-report
# ──────────────────────────────────────────────
@main_bp.route("/download-report")
def download_report():
    from app.services.evaluation_service import generate_markdown_report
    import tempfile

    profile = session.get("profile", {})
    assessment = session.get("session_assessment", {})
    qa_pairs = session.get("qa_pairs", [])

    report = generate_markdown_report(profile, assessment, qa_pairs)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(report)
    tmp.close()

    name = profile.get("name", "candidate").replace(" ", "_")
    return send_file(tmp.name, as_attachment=True,
                     download_name=f"interview_prep_{name}.md",
                     mimetype="text/markdown")


# ──────────────────────────────────────────────
# GET /reset
# ──────────────────────────────────────────────
@main_bp.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("main.index"))
