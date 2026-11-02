"""
app/__init__.py — Flask application factory.
"""
import os
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Make the interview_trainer root importable (for knowledge_base, tools, agent)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Secret key for session signing
    app.secret_key = os.environ.get("SECRET_KEY", "interview-trainer-secret-change-me")

    # Max upload size: 10 MB
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = str(Path(__file__).parent / "static" / "uploads")

    # Server-side session (filesystem) — avoids 4KB cookie limit for large state
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = str(ROOT / "data" / "flask_sessions")
    app.config["SESSION_PERMANENT"] = False

    # Ensure session dir exists
    Path(app.config["SESSION_FILE_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # Extensions
    CORS(app)

    try:
        from flask_session import Session
        Session(app)
    except ImportError:
        pass  # Fall back to cookie sessions if flask-session not installed

    # ── Jinja2 custom filters / tests ──
    app.jinja_env.filters["enumerate"] = enumerate

    @app.template_test("number")
    def is_number(v):
        return isinstance(v, (int, float))

    # Register blueprints / routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
