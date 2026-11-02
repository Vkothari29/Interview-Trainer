"""
run.py — Flask entry point.
Usage: py run.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env next to this file, regardless of the current directory.
load_dotenv(Path(__file__).parent / ".env")

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # The reloader watches the whole environment here, including site-packages
    # (torch/transformers), which restarts the server mid-request and causes
    # intermittent 500s. Keep it opt-in only.
    use_reloader = os.environ.get("FLASK_USE_RELOADER", "0") == "1"
    app.run(debug=True, port=port, use_reloader=use_reloader)
