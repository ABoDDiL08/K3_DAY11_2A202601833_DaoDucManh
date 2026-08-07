"""Reference security boundary for the Day 11 Guards Agent.

This is deliberately framework-independent so students can inspect the policy
and reason about the difference between untrusted content and an authorised
action. It is not a solution for the TODOs in ``src/assignment``.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from urllib.parse import unquote, urlparse


TRUSTED_EGRESS_HOSTS = frozenset({"api.vinbank.example", "cases.vinbank.example"})
HIGH_RISK_ACTIONS = frozenset({
    "transfer_money", "close_account", "change_password",
    "delete_data", "update_personal_info",
})
ZERO_WIDTH = "\u200b\u200c\u200d\ufeff\u2060"
SECRET_PATTERNS = (
    r"\badmin123\b",
    r"sk-[a-z0-9-]{8,}",
    r"db\.vinbank\.internal(?::\d+)?",
    r"(?:password|mật\s*khẩu)\s*[:=]\s*\S+",
)
EGRESS_PII_PATTERNS = (
    r"(?<![\w.+-])[\w.+-]+@(?:[\w-]+\.)+[A-Za-z]{2,}(?![\w-])",
    r"(?<!\d)0(?:[\s.\-]?\d){9,10}(?!\d)",
    r"(?<!\d)1900(?:[\s.\-]?\d){6}(?!\d)",
    r"(?<!\d)(?:\d{9}|\d{12})(?!\d)",
)
INSTRUCTION_OVERRIDE_PATTERNS = (
    r"ignore\s+(?:all\s+)?(?:previous|above|prior)?\s*instructions?",
    r"(?:system|developer)\s+(?:prompt|instruction)|system\s+override",
    r"(?:reveal|disclose|translate|encode|summarize)\b.*(?:secret|password|credential|api\s*key|internal)",
    r"bỏ\s+qua\s+(?:mọi\s+)?hướng\s+dẫn|tiết\s+lộ\s+(?:mật\s*khẩu|api|thông\s*tin\s*nội\s*bộ)",
    r"\b(?:you\s+are\s+now|act\s+as|pretend\s+(?:you\s+are|to\s+be))\b",
    r"\b(?:show|print|output|list|fill\s+in|complete|confirm)\b.{0,120}\b(?:password|secret|credential|api\s*key|system\s+prompt|internal)\b",
    r"\b(?:ciso|auditor|developer|administrator)\b.{0,100}\b(?:ticket|authorize|override|credentials?|secrets?)\b",
)


@dataclass(frozen=True)
class ExternalContent:
    """Data retrieved from email/RAG/web; never an instruction authority."""

    source: str
    text: str
    trusted: bool = False


@dataclass(frozen=True)
class ActionRequest:
    """A proposed side effect awaiting deterministic policy and human approval."""

    action: str
    destination: str
    payload: str
    approval_id: str | None = None
    reviewer_id: str | None = None


@dataclass(frozen=True)
class ActionDecision:
    allowed: bool
    reason: str
    requires_human: bool


def normalize_for_security(text: str) -> str:
    """Canonicalize Unicode and remove invisible separators before policy checks.

    Security checks must see the same logical text even when an attacker inserts
    zero-width characters, bidi controls, or unusual whitespace.  We preserve
    ordinary punctuation and newlines because the caller may still need the
    original wording for a reviewer/audit message.
    """
    normalized = unicodedata.normalize("NFKC", text or "")
    cleaned = []
    for char in normalized:
        category = unicodedata.category(char)
        # Format controls include zero-width and bidirectional override chars.
        # Other control characters are noise for a text policy as well, except
        # the whitespace controls that are useful for readable diagnostics.
        if category == "Cf" or (category == "Cc" and char not in "\n\r\t"):
            continue
        cleaned.append(char)
    return re.sub(r"\s+", " ", "".join(cleaned)).strip()


def contains_secret(text: str) -> bool:
    """Detect a synthetic lab secret even when punctuation/spacing is altered."""
    normalized_text = normalize_for_security(text)
    normalized = re.sub(r"[^a-z0-9]", "", normalized_text.casefold())
    secrets = ("admin123", "skvinbanksecret2024", "dbvinbankinternal")
    return any(secret in normalized for secret in secrets) or any(
        re.search(pattern, normalized_text, re.IGNORECASE)
        for pattern in SECRET_PATTERNS
    )


def contains_instruction_override(text: str) -> bool:
    """Identify instruction-like text after Unicode normalization."""
    normalized = normalize_for_security(text)
    return any(re.search(pattern, normalized, re.IGNORECASE) for pattern in INSTRUCTION_OVERRIDE_PATTERNS)


def assess_external_content(content: ExternalContent) -> ActionDecision:
    """Treat third-party content as data and reject attempts to change policy."""
    if content.trusted:
        return ActionDecision(True, "trusted source metadata", False)
    if contains_instruction_override(content.text):
        return ActionDecision(False, "untrusted content contains an instruction override", False)
    return ActionDecision(True, "untrusted content is data only", False)


def authorize_action(request: ActionRequest) -> ActionDecision:
    """Enforce exact destination allowlist, secret egress block and HITL for risk."""
    try:
        destination = urlparse(request.destination)
        port = destination.port
    except (TypeError, ValueError):
        return ActionDecision(False, "destination is malformed", False)

    hostname = (destination.hostname or "").casefold()
    if (
        destination.scheme.lower() != "https"
        or hostname not in TRUSTED_EGRESS_HOSTS
        or port not in (None, 443)
        or destination.username
        or destination.password
        or any(char.isspace() or ord(char) < 32 for char in request.destination)
    ):
        return ActionDecision(False, "destination is not allowlisted", False)
    normalized_payload = normalize_for_security(request.payload)
    destination_data = normalize_for_security(
        unquote(destination.path or "") + " " + unquote(destination.query or "")
    )
    if contains_secret(normalized_payload) or contains_secret(destination_data) or any(
        re.search(pattern, normalized_payload + " " + destination_data, re.IGNORECASE)
        for pattern in EGRESS_PII_PATTERNS
    ):
        return ActionDecision(False, "payload contains protected data", False)
    if request.action in HIGH_RISK_ACTIONS:
        approved = bool(
            request.reviewer_id
            and request.approval_id
            and re.fullmatch(r"HITL-[A-Z0-9]{8}", request.approval_id)
        )
        if not approved:
            return ActionDecision(False, "high-risk action needs recorded human approval", True)
    return ActionDecision(True, "least-privilege policy permits this action", False)
