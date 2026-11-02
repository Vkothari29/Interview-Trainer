"""
Interview Trainer Agent — Streamlit UI (Modern, theme-adaptive)
Run with: py -m streamlit run app.py
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Trainer Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Modern, theme-adaptive CSS
# Uses CSS variables so it works in both light and dark mode
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base resets ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--background-color) !important;
    border-right: 1px solid var(--secondary-background-color);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}

/* ── Hero header ── */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white !important;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
    width: fit-content;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin: 0 0 10px 0;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--text-color);
    opacity: 0.65;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* ── Cards ── */
.card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.card:hover {
    box-shadow: 0 4px 20px rgba(99,102,241,0.12);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.75rem;
}

/* ── Stat chips (feature list) ── */
.chip-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.5rem;
}
.chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(99,102,241,0.1);
    color: #6366f1;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 4px 12px;
}

/* ── Chat bubbles ── */
.bubble-coach {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 0 16px 16px 16px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    position: relative;
    line-height: 1.7;
}
.bubble-coach::before {
    content: "🤖";
    position: absolute;
    top: -10px;
    left: -6px;
    font-size: 1.1rem;
}
.bubble-user {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.10));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px 0 16px 16px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    text-align: right;
    line-height: 1.7;
}

/* ── Score bar ── */
.score-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 6px 18px;
    border-radius: 24px;
}
.score-bar-track {
    background: rgba(128,128,128,0.15);
    border-radius: 8px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.score-bar-fill {
    height: 8px;
    border-radius: 8px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.6s ease;
}

/* ── Tip box ── */
.tip-box {
    background: rgba(245,158,11,0.08);
    border-left: 3px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
    line-height: 1.6;
    margin-top: 0.5rem;
}

/* ── Section divider ── */
.section-divider {
    height: 1px;
    background: rgba(128,128,128,0.12);
    margin: 1.5rem 0;
    border: none;
}

/* ── Progress label ── */
.progress-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #6366f1;
    letter-spacing: 0.04em;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.5rem;
}
.sidebar-brand-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}
.sidebar-brand-text {
    font-weight: 700;
    font-size: 1rem;
    line-height: 1.2;
}
.sidebar-brand-sub {
    font-size: 0.72rem;
    opacity: 0.55;
}

/* ── Step indicator ── */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 0.85rem;
}
.step-num {
    min-width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.step-text {
    font-size: 0.85rem;
    line-height: 1.5;
    opacity: 0.85;
}

/* ── Form inputs — remove Streamlit's default blue border in favour of purple ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 10px !important;
    border-color: rgba(128,128,128,0.25) !important;
    transition: border-color 0.2s !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

/* ── Primary button ── */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    padding: 0.55rem 1.25rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ── */
div.stButton > button[kind="secondary"],
div.stFormSubmitButton > button[kind="secondary"] {
    border-radius: 10px !important;
    border-color: rgba(128,128,128,0.3) !important;
    font-weight: 500 !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 14px;
    padding: 1rem 1.25rem !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em !important;
    opacity: 0.6;
}
div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* ── Expander ── */
details {
    border: 1px solid rgba(128,128,128,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden;
    margin-bottom: 0.5rem !important;
}
details summary {
    font-weight: 600 !important;
    padding: 0.75rem 1rem !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    background: rgba(99,102,241,0.03) !important;
    padding: 0.5rem !important;
}

/* ── Alerts / info boxes — make them adaptive ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ── Hide the hamburger menu deploy button clutter ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state helpers
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "profile",
        "session": None,
        "profile": {},
        "resume_profile": None,
        "chat_history": [],
        "awaiting_answer": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🎯</div>
        <div>
            <div class="sidebar-brand-text">Interview Trainer</div>
            <div class="sidebar-brand-sub">RAG-Powered AI Coach</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.page != "profile":
        if st.button("← Start Over", use_container_width=True):
            for key in ["session", "profile", "resume_profile", "chat_history"]:
                st.session_state[key] = None if key != "chat_history" else []
            st.session_state.awaiting_answer = False
            st.session_state.page = "profile"
            st.rerun()
        st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    st.markdown('<div class="card-title">How it works</div>', unsafe_allow_html=True)
    steps = [
        ("Set up profile", "Add your role, level & optional resume"),
        ("Start interview", "Answer questions one by one"),
        ("Get feedback", "STAR coaching + instant scores"),
        ("Review results", "Readiness score & action plan"),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step-row">
            <div class="step-num">{i}</div>
            <div class="step-text"><strong>{title}</strong><br>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Powered by</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="chip-grid">
        <span class="chip">⚡ Groq</span>
        <span class="chip">✨ Gemini</span>
        <span class="chip">🔗 LangGraph</span>
        <span class="chip">🔍 ChromaDB</span>
    </div>
    <br><span style="font-size:0.75rem;opacity:0.5;">100% free to run</span>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Page: Profile Setup
# ─────────────────────────────────────────────
def page_profile():
    # Hero
    st.markdown("""
    <div class="hero-badge">✦ AI Interview Coach</div>
    <div class="hero-title">Ace Your Next Interview</div>
    <div class="hero-sub">
        Personalized mock interviews powered by RAG — tailored to your role,
        experience level, and resume. Get real feedback, not generic tips.
    </div>
    """, unsafe_allow_html=True)

    col_form, col_side = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="card-title">Your Profile</div>', unsafe_allow_html=True)

        name = st.text_input(
            "Full Name",
            placeholder="e.g. Alex Johnson",
            key="inp_name",
        )
        role = st.text_input(
            "Target Job Role / Title",
            placeholder="e.g. Software Engineer, Data Scientist, Product Manager",
            key="inp_role",
        )
        level = st.selectbox(
            "Experience Level",
            ["Fresher", "Junior", "Mid-level", "Senior", "Lead"],
            index=2,
            key="inp_level",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            focus = st.selectbox(
                "Focus Area",
                ["All", "Technical", "Behavioral", "System Design", "HR"],
                key="inp_focus",
            )
        with col_b:
            difficulty = st.selectbox(
                "Difficulty",
                ["Mixed", "Easy", "Medium", "Hard"],
                key="inp_difficulty",
            )

        st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Resume (optional)</div>', unsafe_allow_html=True)
        st.caption("Upload your resume for truly personalized questions based on your projects and skills.")
        resume_file = st.file_uploader(
            "Drag & drop or browse",
            type=["pdf", "docx", "doc", "txt"],
            key="inp_resume",
            label_visibility="collapsed",
        )
        if resume_file:
            st.success(f"📄 **{resume_file.name}** ready to parse")

        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button(
            "Start Mock Interview →",
            type="primary",
            use_container_width=True,
            key="start_btn",
        )

    with col_side:
        # Feature chips
        st.markdown("""
        <div class="card">
            <div class="card-title">What you'll get</div>
            <div class="chip-grid">
                <span class="chip">✅ 10 tailored questions</span>
                <span class="chip">📊 Instant scoring</span>
                <span class="chip">⭐ STAR coaching</span>
                <span class="chip">💡 Model answers</span>
                <span class="chip">🔁 Follow-up questions</span>
                <span class="chip">📈 Readiness score</span>
                <span class="chip">📥 Export report</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <div class="card-title">Pro Tips</div>
            <div class="step-row">
                <div class="step-num">💡</div>
                <div class="step-text">Be specific — <em>"Backend Engineer"</em> beats just <em>"Engineer"</em></div>
            </div>
            <div class="step-row">
                <div class="step-num">📄</div>
                <div class="step-text">Upload your resume to unlock project-specific questions</div>
            </div>
            <div class="step-row">
                <div class="step-num">🎯</div>
                <div class="step-text">Choose <em>Mixed</em> difficulty for a realistic interview feel</div>
            </div>
            <div class="step-row">
                <div class="step-num">🌟</div>
                <div class="step-text">Answer as you would in a real interview — don't self-censor</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Level guide
        level_map = {
            "Fresher": "Fundamentals, projects, internships, learning attitude",
            "Junior": "Core concepts, basic system thinking, code quality",
            "Mid-level": "Depth, ownership, system design intro, debugging",
            "Senior": "Architecture, trade-offs, cross-team impact, mentoring",
            "Lead": "Strategy, people management, technical vision",
        }
        current_level = st.session_state.get("inp_level", "Mid-level")
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Level Guide — {current_level}</div>
            <div class="step-text">{level_map.get(current_level, '')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Handle start
    if start_btn:
        if not name.strip():
            st.error("Please enter your name.")
            return
        if not role.strip():
            st.error("Please enter your target role.")
            return

        resume_summary = None
        if resume_file:
            with st.spinner("Parsing your resume with AI..."):
                try:
                    from tools.resume_parser import parse_resume
                    rb = resume_file.read()
                    rp = parse_resume(rb, resume_file.name)
                    st.session_state.resume_profile = rp
                    resume_summary = rp.summary
                    if rp.skills:
                        resume_summary += f" Key skills: {', '.join(rp.skills[:5])}."
                except Exception as e:
                    st.warning(f"Resume parsing failed ({e}). Continuing without it.")

        st.session_state.profile = {
            "name": name.strip(),
            "role": role.strip(),
            "level": level,
            "focus": None if focus == "All" else focus,
            "difficulty": None if difficulty == "Mixed" else difficulty,
            "resume_summary": resume_summary,
        }

        with st.spinner("Preparing your personalized interview..."):
            try:
                from agent.coach_agent import InterviewSession
                session = InterviewSession(**st.session_state.profile, max_followups=1)
                messages = session.start()
                st.session_state.session = session
                st.session_state.chat_history = messages
                st.session_state.awaiting_answer = True
                st.session_state.page = "interview"
                st.rerun()
            except Exception as e:
                st.error(f"Failed to start session: {e}")
                st.exception(e)


# ─────────────────────────────────────────────
# Page: Interview
# ─────────────────────────────────────────────
def render_message(msg: dict):
    role = msg["role"]
    content = msg["content"]
    if role == "coach":
        st.markdown(f'<div class="bubble-coach">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-user"><strong>You</strong><br>{content}</div>', unsafe_allow_html=True)


def page_interview():
    session = st.session_state.session
    profile = st.session_state.profile
    resume_profile = st.session_state.resume_profile

    # Top bar
    total = session.total_questions
    done = min(session.current_question_index, total)

    top_left, top_right = st.columns([3, 1])
    with top_left:
        pct = int((done / total * 100) if total else 0)
        st.markdown(f"""
        <div class="progress-label">Question {done} of {total} &nbsp;·&nbsp; {pct}% complete</div>
        """, unsafe_allow_html=True)
        st.progress(done / total if total else 0)
    with top_right:
        st.markdown(f"""
        <div style="text-align:right;font-size:0.85rem;opacity:0.7;padding-top:4px;">
            <strong>{profile['name']}</strong><br>
            {profile['level']} · {profile['role']}
        </div>
        """, unsafe_allow_html=True)

    # Resume mini card
    if resume_profile:
        with st.expander("Your parsed resume", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Experience:** {resume_profile.years_of_experience or 'N/A'} yrs")
            with c2:
                if resume_profile.programming_languages:
                    st.markdown(f"**Languages:** {', '.join(resume_profile.programming_languages[:4])}")
            with c3:
                if resume_profile.frameworks:
                    st.markdown(f"**Frameworks:** {', '.join(resume_profile.frameworks[:4])}")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # Chat
    for msg in st.session_state.chat_history:
        render_message(msg)

    # Answer input
    if not session.is_done and st.session_state.awaiting_answer:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("answer_form", clear_on_submit=True):
            user_answer = st.text_area(
                "Your answer",
                placeholder="Type your answer here. Be as detailed as you would in a real interview...",
                height=140,
                key="answer_input",
                label_visibility="collapsed",
            )
            c_submit, c_skip = st.columns([5, 1])
            with c_submit:
                submitted = st.form_submit_button(
                    "Submit Answer →",
                    type="primary",
                    use_container_width=True,
                )
            with c_skip:
                skipped = st.form_submit_button("Skip", use_container_width=True)

        if submitted and user_answer.strip():
            with st.spinner("Evaluating your answer..."):
                new_msgs = session.submit_answer(user_answer.strip())
                st.session_state.chat_history.extend(new_msgs)
                if session.is_done:
                    st.session_state.awaiting_answer = False
                    st.session_state.page = "results"
                st.rerun()
        elif skipped:
            with st.spinner("Moving on..."):
                new_msgs = session.submit_answer("I'll skip this question.")
                st.session_state.chat_history.extend(new_msgs)
                if session.is_done:
                    st.session_state.awaiting_answer = False
                    st.session_state.page = "results"
                st.rerun()

    elif session.is_done:
        st.session_state.page = "results"
        st.rerun()


# ─────────────────────────────────────────────
# Page: Results
# ─────────────────────────────────────────────
def page_results():
    session = st.session_state.session
    profile = st.session_state.profile
    assessment = session.assessment or {}

    score = assessment.get("readiness_score", 0)
    grade_label = (
        "Excellent" if score >= 80 else
        "Good" if score >= 65 else
        "Needs Practice" if score >= 50 else
        "Keep Going"
    )
    grade_color = (
        "#22c55e" if score >= 80 else
        "#6366f1" if score >= 65 else
        "#f59e0b" if score >= 50 else
        "#ef4444"
    )

    # Hero result
    st.markdown(f"""
    <div class="hero-title" style="font-size:1.9rem;">Interview Complete!</div>
    <div class="hero-sub">{profile['name']} &nbsp;·&nbsp; {profile['level']} {profile['role']}</div>
    """, unsafe_allow_html=True)

    # Score + grade
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Readiness Score", f"{score}/100")
    with c2:
        st.metric("Questions Done", len(session.state.get("qa_pairs", [])))
    with c3:
        st.metric("Assessment", grade_label)

    # Score bar
    st.markdown(f"""
    <div style="margin: 1rem 0 0.5rem 0; font-size: 0.8rem; font-weight:600; opacity:0.6;">
        OVERALL READINESS
    </div>
    <div class="score-bar-track">
        <div class="score-bar-fill" style="width:{score}%; background: linear-gradient(90deg, {grade_color}, {grade_color}aa);"></div>
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<div class="card-title">Top Strengths</div>', unsafe_allow_html=True)
        for s in assessment.get("strengths", []):
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num" style="background:linear-gradient(135deg,#22c55e,#16a34a);">✓</div>
                <div class="step-text">{s}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">Summary</div>', unsafe_allow_html=True)
        st.info(assessment.get("summary", "Session complete."))

    with col_r:
        st.markdown('<div class="card-title">Priority Improvements</div>', unsafe_allow_html=True)
        for w in assessment.get("weak_areas", []):
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num" style="background:linear-gradient(135deg,#f59e0b,#d97706);">↑</div>
                <div class="step-text">{w}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">Recommended Next Steps</div>', unsafe_allow_html=True)
        for i, n in enumerate(assessment.get("next_steps", []), 1):
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num">{i}</div>
                <div class="step-text">{n}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # Q&A breakdown
    st.markdown('<div class="card-title">Question-by-Question Breakdown</div>', unsafe_allow_html=True)
    qa_pairs = session.state.get("qa_pairs", [])
    for i, pair in enumerate(qa_pairs):
        score_obj = pair.get("score")
        overall = score_obj.overall if score_obj else 0
        dot = "🟢" if overall >= 75 else "🟡" if overall >= 55 else "🔴"

        with st.expander(f"{dot} Q{i+1} — {pair['question'][:72]}... ({overall}/100)"):
            st.markdown(f"**Your answer:** {pair['answer']}")
            st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
            if score_obj:
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Relevance", f"{score_obj.relevance}/10")
                m2.metric("Structure", f"{score_obj.structure_clarity}/10")
                m3.metric("Depth", f"{score_obj.depth_accuracy}/10")
                m4.metric("STAR", f"{score_obj.star_usage}/10")
                m5.metric("Confidence", f"{score_obj.confidence_indicators}/10")

                st.markdown(
                    "**Strengths:** " + " &nbsp;·&nbsp; ".join(score_obj.strengths),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "**Improve:** " + " &nbsp;·&nbsp; ".join(score_obj.improvements),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="tip-box">💡 {score_obj.model_tip}</div>',
                    unsafe_allow_html=True,
                )
                if score_obj.improved_answer_snippet:
                    st.markdown(f"**Stronger phrasing:** *{score_obj.improved_answer_snippet}*")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # Export
    col_exp, col_restart = st.columns(2)
    with col_exp:
        report = _generate_markdown_report(profile, assessment, qa_pairs)
        st.download_button(
            label="Download Prep Report (Markdown)",
            data=report,
            file_name=f"interview_prep_{profile['name'].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_restart:
        if st.button("Practice Again →", type="primary", use_container_width=True):
            for key in ["session", "profile", "resume_profile", "chat_history"]:
                st.session_state[key] = None if key != "chat_history" else []
            st.session_state.awaiting_answer = False
            st.session_state.page = "profile"
            st.rerun()


def _generate_markdown_report(profile: dict, assessment: dict, qa_pairs: list) -> str:
    lines = [
        "# Interview Preparation Report",
        f"**Name:** {profile['name']}  ",
        f"**Role:** {profile['level']} {profile['role']}  ",
        f"**Readiness Score:** {assessment.get('readiness_score', 0)}/100\n",
        f"## Summary\n{assessment.get('summary', '')}\n",
        "## Strengths\n" + "\n".join(f"- {s}" for s in assessment.get("strengths", [])) + "\n",
        "## Priority Improvements\n" + "\n".join(f"- {w}" for w in assessment.get("weak_areas", [])) + "\n",
        "## Recommended Next Steps\n" + "\n".join(f"- {n}" for n in assessment.get("next_steps", [])) + "\n",
        "---\n## Question & Answer Review\n",
    ]
    for i, pair in enumerate(qa_pairs):
        s = pair.get("score")
        lines.append(f"### Q{i+1}: {pair['question']}")
        lines.append(f"**Your Answer:** {pair['answer']}\n")
        if s:
            lines.append(f"**Score:** {s.overall}/100")
            lines.append(f"**Strengths:** {' | '.join(s.strengths)}")
            lines.append(f"**Improve:** {' | '.join(s.improvements)}")
            lines.append(f"**Tip:** {s.model_tip}\n")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────
page = st.session_state.page
if page == "profile":
    page_profile()
elif page == "interview":
    page_interview()
elif page == "results":
    page_results()
