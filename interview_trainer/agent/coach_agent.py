"""
Main Interview Coach Agent — LangGraph-powered state machine.
Orchestrates the full mock interview lifecycle:
  SETUP → ASKING → EVALUATING → FOLLOW_UP → NEXT_QUESTION → DONE
"""

import os
import sys
from pathlib import Path
from typing import Annotated, Optional, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.question_generator import generate_question_set, generate_followup_questions
from tools.evaluator import evaluate_answer, coach_star_answer, generate_session_assessment, AnswerScore


# ─────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────

class SessionState(TypedDict):
    # User profile
    name: str
    role: str
    level: str
    focus: Optional[str]
    difficulty: Optional[str]
    resume_summary: Optional[str]

    # Session data
    questions: list[dict]           # Full question objects
    current_index: int              # Which question we're on
    followup_count: int             # Follow-ups asked for current question
    max_followups: int

    # Conversation
    messages: list[dict]            # {role: "coach"|"user", content: str}
    last_user_answer: str

    # Evaluation results
    qa_pairs: list[dict]            # [{question, answer, score: AnswerScore}]

    # Control
    phase: str                      # setup | asking | awaiting_answer | evaluating | followup | done
    session_assessment: Optional[dict]


# ─────────────────────────────────────────────
# LLM helpers
# ─────────────────────────────────────────────

def _get_llm():
    """Fast Groq for conversational turns; Gemini as backup."""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and not groq_key.startswith("your_"):
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                groq_api_key=groq_key,
                temperature=0.5,
            )
        except Exception:
            pass
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if gemini_key and not gemini_key.startswith("your_"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            google_api_key=gemini_key,
            temperature=0.5,
        )
    return None


# ─────────────────────────────────────────────
# Node Functions
# ─────────────────────────────────────────────

def node_start_session(state: SessionState) -> SessionState:
    """Load questions and compose the opening coach message."""
    questions = generate_question_set(
        name=state["name"],
        role=state["role"],
        level=state["level"],
        focus=state.get("focus"),
        difficulty=state.get("difficulty"),
        resume_summary=state.get("resume_summary"),
        n_questions=10,
    )

    opening = (
        f"Hi {state['name']}! 👋 I'm your Interview Coach.\n\n"
        f"I've prepared a personalized mock interview for a **{state['level']} {state['role']}** role. "
        f"We'll cover {len(questions)} questions — a mix of Technical, Behavioral, and HR.\n\n"
        "A few ground rules:\n"
        "- Answer each question as you would in a real interview.\n"
        "- I'll ask follow-up questions if needed.\n"
        "- At the end, I'll give you detailed feedback and a readiness score.\n\n"
        "Ready? Let's begin with the first question."
    )

    return {
        **state,
        "questions": questions,
        "current_index": 0,
        "followup_count": 0,
        "messages": [{"role": "coach", "content": opening}],
        "qa_pairs": [],
        "phase": "asking",
    }


def node_ask_question(state: SessionState) -> SessionState:
    """Emit the current question to the user."""
    idx = state["current_index"]
    questions = state["questions"]

    if idx >= len(questions):
        return {**state, "phase": "done"}

    q = questions[idx]
    cat_emoji = {"Technical": "🔧", "Behavioral": "💬", "HR": "🧑‍💼"}.get(q["category"], "❓")
    msg = (
        f"**Question {idx + 1} of {len(questions)}** {cat_emoji} *{q['category']} | {q['difficulty']}*\n\n"
        f"{q['question']}"
    )
    messages = state["messages"] + [{"role": "coach", "content": msg}]
    return {**state, "messages": messages, "phase": "awaiting_answer"}


def node_receive_answer(state: SessionState, user_answer: str) -> SessionState:
    """Record the user's answer and transition to evaluation."""
    messages = state["messages"] + [{"role": "user", "content": user_answer}]
    return {**state, "messages": messages, "last_user_answer": user_answer, "phase": "evaluating"}


def node_evaluate_answer(state: SessionState) -> SessionState:
    """Evaluate the user's answer and optionally ask follow-ups."""
    idx = state["current_index"]
    q = state["questions"][idx]
    user_answer = state["last_user_answer"]

    score: AnswerScore = evaluate_answer(
        question=q["question"],
        user_answer=user_answer,
        model_answer=q["model_answer"],
        category=q["category"],
        level=state["level"],
        role=state["role"],
    )

    # Build inline feedback message (shown after follow-ups or at end)
    # For now, store and decide whether to follow up
    qa_pairs = state["qa_pairs"] + [
        {"question": q["question"], "answer": user_answer, "score": score, "category": q["category"]}
    ]

    # Decide follow-up
    should_followup = (
        state["followup_count"] < state["max_followups"]
        and score.overall < 80
        and len(user_answer.split()) > 10
    )

    new_phase = "followup" if should_followup else "next_question"
    return {**state, "qa_pairs": qa_pairs, "phase": new_phase}


def node_ask_followup(state: SessionState) -> SessionState:
    """Generate and ask an intelligent follow-up question."""
    idx = state["current_index"]
    q = state["questions"][idx]
    user_answer = state["last_user_answer"]

    followups = generate_followup_questions(
        original_question=q["question"],
        user_answer=user_answer,
        role=state["role"],
        level=state["level"],
        n=1,
    )
    followup_q = followups[0] if followups else "Can you expand on that with a specific example?"

    msg = f"**Follow-up:** {followup_q}"
    messages = state["messages"] + [{"role": "coach", "content": msg}]
    return {
        **state,
        "messages": messages,
        "followup_count": state["followup_count"] + 1,
        "phase": "awaiting_answer",
    }


def node_give_feedback(state: SessionState) -> SessionState:
    """Show the score and feedback for the current question, then advance."""
    idx = state["current_index"]
    q = state["questions"][idx]
    score: AnswerScore = state["qa_pairs"][-1]["score"]

    bar = "█" * (score.overall // 10) + "░" * (10 - score.overall // 10)
    feedback_lines = [
        f"\n**Feedback for Q{idx + 1}:** `{bar}` **{score.overall}/100**\n",
        f"✅ **Strengths:** {' | '.join(score.strengths)}",
        f"📈 **Improve:** {' | '.join(score.improvements)}",
        f"💡 **Tip:** {score.model_tip}",
    ]
    if score.improved_answer_snippet:
        feedback_lines.append(f"\n📝 **Stronger phrasing:** _{score.improved_answer_snippet}_")

    # STAR coaching for behavioral questions
    if q["category"] == "Behavioral" and score.star_breakdown:
        sb = score.star_breakdown
        star_scores = " | ".join(f"{k.capitalize()}: {v}/10" for k, v in sb.items() if isinstance(v, int))
        feedback_lines.append(f"\n⭐ **STAR Breakdown:** {star_scores}")

    feedback_msg = "\n".join(feedback_lines)
    messages = state["messages"] + [{"role": "coach", "content": feedback_msg}]
    return {
        **state,
        "messages": messages,
        "current_index": idx + 1,
        "followup_count": 0,
        "phase": "asking",
    }


def node_wrap_up(state: SessionState) -> SessionState:
    """Generate the final session assessment."""
    assessment = generate_session_assessment(
        qa_pairs=state["qa_pairs"],
        name=state["name"],
        role=state["role"],
        level=state["level"],
    )

    score = assessment.get("readiness_score", 0)
    bar = "█" * (score // 10) + "░" * (10 - score // 10)
    lines = [
        f"## 🎉 Mock Interview Complete!\n",
        f"**Readiness Score:** `{bar}` **{score}/100**\n",
        f"_{assessment.get('summary', '')}_\n",
        f"### ✅ Top Strengths",
        "\n".join(f"- {s}" for s in assessment.get("strengths", [])),
        f"\n### 📈 Priority Improvements",
        "\n".join(f"- {w}" for w in assessment.get("weak_areas", [])),
        f"\n### 🚀 Next Steps",
        "\n".join(f"- {n}" for n in assessment.get("next_steps", [])),
    ]

    wrap_msg = "\n".join(lines)
    messages = state["messages"] + [{"role": "coach", "content": wrap_msg}]
    return {
        **state,
        "messages": messages,
        "session_assessment": assessment,
        "phase": "done",
    }


# ─────────────────────────────────────────────
# Graph Construction
# ─────────────────────────────────────────────

def build_interview_graph() -> StateGraph:
    graph = StateGraph(SessionState)

    graph.add_node("start_session", node_start_session)
    graph.add_node("ask_question", node_ask_question)
    graph.add_node("evaluate_answer", node_evaluate_answer)
    graph.add_node("ask_followup", node_ask_followup)
    graph.add_node("give_feedback", node_give_feedback)
    graph.add_node("wrap_up", node_wrap_up)

    graph.set_entry_point("start_session")
    graph.add_edge("start_session", "ask_question")

    # After asking: wait for user input externally; the UI calls node_receive_answer then evaluate
    graph.add_conditional_edges(
        "evaluate_answer",
        lambda s: s["phase"],
        {
            "followup": "ask_followup",
            "next_question": "give_feedback",
        },
    )
    graph.add_edge("ask_followup", "evaluate_answer")

    graph.add_conditional_edges(
        "give_feedback",
        lambda s: "wrap_up" if s["current_index"] >= len(s["questions"]) else "ask_question",
        {
            "wrap_up": "wrap_up",
            "ask_question": "ask_question",
        },
    )

    graph.add_edge("wrap_up", END)
    return graph


# ─────────────────────────────────────────────
# Session Manager (used by Streamlit UI)
# ─────────────────────────────────────────────

class InterviewSession:
    """
    High-level session manager for the Streamlit UI.
    Manages state manually for the interactive (pause-and-wait) interview loop.
    """

    def __init__(
        self,
        name: str,
        role: str,
        level: str,
        focus: Optional[str] = None,
        difficulty: Optional[str] = None,
        resume_summary: Optional[str] = None,
        max_followups: int = 1,
    ):
        self.state: SessionState = {
            "name": name,
            "role": role,
            "level": level,
            "focus": focus,
            "difficulty": difficulty,
            "resume_summary": resume_summary,
            "questions": [],
            "current_index": 0,
            "followup_count": 0,
            "max_followups": max_followups,
            "messages": [],
            "last_user_answer": "",
            "qa_pairs": [],
            "phase": "setup",
            "session_assessment": None,
        }

    def start(self) -> list[dict]:
        """Initialize session, load questions, return opening messages."""
        self.state = node_start_session(self.state)
        self.state = node_ask_question(self.state)
        return self.state["messages"]

    def submit_answer(self, user_answer: str) -> list[dict]:
        """
        Process user answer: evaluate → (follow-up or feedback) → next question.
        Returns only the NEW messages added in this turn.
        """
        prev_len = len(self.state["messages"])

        self.state = node_receive_answer(self.state, user_answer)
        self.state = node_evaluate_answer(self.state)

        if self.state["phase"] == "followup":
            self.state = node_ask_followup(self.state)
        else:
            self.state = node_give_feedback(self.state)
            if self.state["phase"] == "asking":
                if self.state["current_index"] < len(self.state["questions"]):
                    self.state = node_ask_question(self.state)
                else:
                    self.state = node_wrap_up(self.state)

        return self.state["messages"][prev_len:]

    @property
    def is_done(self) -> bool:
        return self.state["phase"] == "done"

    @property
    def messages(self) -> list[dict]:
        return self.state["messages"]

    @property
    def assessment(self) -> Optional[dict]:
        return self.state.get("session_assessment")

    @property
    def current_question_index(self) -> int:
        return self.state["current_index"]

    @property
    def total_questions(self) -> int:
        return len(self.state["questions"])
