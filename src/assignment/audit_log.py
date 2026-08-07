"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agents.security_boundary import contains_secret


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """Record a request start and return its correlation ID.

        Audit data is itself a sensitive sink. We retain enough text for
        forensics while masking known credentials, API keys, emails and phone
        numbers before export.
        """
        correlation_id = request_id or f"req-{uuid.uuid4().hex}"
        started = datetime.now(timezone.utc)
        self._open[correlation_id] = started.timestamp()
        self.logs.append(
            {
                "event": "input",
                "request_id": correlation_id,
                "user_id": user_id,
                "timestamp": started.isoformat(),
                "text": _redact_audit_text(text),
            }
        )
        return correlation_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """Record the terminal decision and correlate it with the input."""
        correlation_id = request_id or f"req-{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        started_at = self._open.pop(correlation_id, now.timestamp())
        latency_ms = max(0.0, (now.timestamp() - started_at) * 1000.0)
        self.logs.append(
            {
                "event": "output",
                "request_id": correlation_id,
                "user_id": user_id,
                "timestamp": now.isoformat(),
                "text": _redact_audit_text(text),
                "blocked": bool(blocked),
                "layer": layer,
                "latency_ms": round(latency_ms, 3),
            }
        )
        return correlation_id

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array), creating the parent directory."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.logs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redact_audit_text(text: str) -> str:
    """Mask common secrets/PII before putting text into an audit artifact."""
    value = str(text or "")
    value = re.sub(r"\badmin123\b", "[REDACTED]", value, flags=re.IGNORECASE)
    value = re.sub(r"\bsk-[A-Za-z0-9-]{8,}\b", "[REDACTED]", value)
    value = re.sub(r"\b[a-z0-9.-]+\.internal(?::\d+)?\b", "[REDACTED]", value, flags=re.IGNORECASE)
    value = re.sub(r"(?<!\d)0(?:[\s.\-]?\d){9,10}(?!\d)", "[REDACTED]", value)
    value = re.sub(r"(?<![\w.+-])[\w.+-]+@(?:[\w-]+\.)+[A-Za-z]{2,}(?![\w-])", "[REDACTED]", value)
    value = re.sub(r"\b(?:admin\s+)?password\s*(?:is|=|:)\s*[^\s,.;]+", "password=[REDACTED]", value, flags=re.IGNORECASE)
    # A final canary check documents the invariant for future extensions.
    if contains_secret(value):
        value = "[REDACTED_SENSITIVE_AUDIT_TEXT]"
    return value
