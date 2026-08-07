"""
Lab 11 — Configuration & API Key Setup
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed in requirements
    load_dotenv = None


def setup_api_key():
    """Load Google API key from environment or prompt."""
    # Load the repository .env without overriding an explicitly configured
    # environment variable. This makes the documented PowerShell workflow
    # work in a fresh terminal while keeping secrets out of source control.
    if load_dotenv is not None:
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
    if not os.environ.get("GOOGLE_API_KEY", "").strip():
        os.environ["GOOGLE_API_KEY"] = input("Enter Google API Key: ")
    if not os.environ.get("GOOGLE_API_KEY", "").strip():
        raise RuntimeError("GOOGLE_API_KEY is required to run the live agent")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    # NeMo 0.23+ needs its LangChain integration for the Google GenAI
    # backend.  Keep an explicit caller override, but make the documented
    # `python main.py --part 2` workflow use the compatible adapter by default.
    os.environ.setdefault("NEMOGUARDRAILS_LLM_FRAMEWORK", "langchain")
    print("API key loaded.")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
