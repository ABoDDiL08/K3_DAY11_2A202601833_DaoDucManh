"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 11: Confidence Router
  TODO 12: Design 3 HITL decision points
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import uuid


# ============================================================
# TODO 11: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        action = (action_type or "general").casefold()
        try:
            score = float(confidence)
        except (TypeError, ValueError):
            score = float("nan")

        # Invalid confidence, an empty response, and a high-risk action all
        # fail closed. Confidence is advisory; it is never permission to
        # bypass a deterministic risk policy.
        if action in {item.casefold() for item in HIGH_RISK_ACTIONS}:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action: {action_type}",
                priority="high",
                requires_human=True,
            )
        if not math.isfinite(score) or score < 0.0 or score > 1.0:
            return RoutingDecision(
                action="escalate",
                confidence=0.0 if not math.isfinite(score) else score,
                reason="Invalid confidence — escalating for human review",
                priority="high",
                requires_human=True,
            )
        if not (response or "").strip():
            return RoutingDecision(
                action="escalate",
                confidence=score,
                reason="Empty response — escalating for human review",
                priority="high",
                requires_human=True,
            )
        if score >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=score,
                reason="High confidence",
                priority="low",
                requires_human=False,
            )
        if score >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=score,
                reason="Medium confidence — needs review",
                priority="normal",
                requires_human=True,
            )
        return RoutingDecision(
            action="escalate",
            confidence=score,
            reason="Low confidence — escalating",
            priority="high",
            requires_human=True,
        )


@dataclass
class HITLReview:
    """A review record whose default outcome is not approved."""

    review_id: str
    request_id: str
    intent: str
    proposed_action: str
    context: dict
    diff: dict
    created_at: str
    expires_at: str
    status: str = "pending"
    reviewer_id: str | None = None
    decision_reason: str | None = None
    approval_id: str | None = None
    integrity_hash: str | None = None


class HITLReviewQueue:
    """Minimal, auditable approve/reject/timeout lifecycle.

    The queue is intentionally fail-closed: pending and timeout records are
    never treated as approval, and approval requires an identified reviewer.
    """

    def __init__(self, default_timeout_seconds: int = 300):
        if default_timeout_seconds <= 0:
            raise ValueError("default_timeout_seconds must be positive")
        self.default_timeout_seconds = default_timeout_seconds
        self.reviews: dict[str, HITLReview] = {}

    @staticmethod
    def _fingerprint(review: HITLReview) -> str:
        """Hash the exact decision material shown to the reviewer.

        HITL is a security boundary only if the text approved is the text
        executed. The hash covers nested context/diff values and is checked
        again immediately before approval.
        """
        material = {
            "request_id": review.request_id,
            "intent": review.intent,
            "proposed_action": review.proposed_action,
            "context": review.context,
            "diff": review.diff,
        }
        canonical = json.dumps(
            material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def _expire_if_needed(review: HITLReview) -> bool:
        """Mark a pending review expired; malformed timestamps fail closed."""
        if review.status != "pending":
            return review.status == "timeout"
        try:
            expires_at = datetime.fromisoformat(review.expires_at)
        except (TypeError, ValueError):
            review.status = "timeout"
            review.decision_reason = "invalid expiry timestamp"
            return True
        if datetime.now(timezone.utc) >= expires_at:
            review.status = "timeout"
            review.decision_reason = "review timeout"
            return True
        return False

    def submit(
        self,
        *,
        request_id: str,
        intent: str,
        proposed_action: str,
        context: dict | None = None,
        diff: dict | None = None,
        timeout_seconds: int | None = None,
    ) -> HITLReview:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=timeout_seconds or self.default_timeout_seconds)
        review = HITLReview(
            review_id=f"review-{uuid.uuid4().hex}",
            request_id=request_id,
            intent=intent,
            proposed_action=proposed_action,
            context=dict(context or {}),
            diff=dict(diff or {}),
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )
        review.integrity_hash = self._fingerprint(review)
        self.reviews[review.review_id] = review
        return review

    def decide(
        self,
        review_id: str,
        decision: str,
        *,
        reviewer_id: str | None,
        reason: str = "",
    ) -> HITLReview:
        review = self.reviews[review_id]
        if review.status != "pending":
            raise ValueError(f"review is already {review.status}")
        if self._expire_if_needed(review):
            raise ValueError("review has expired; approval denied")
        if not review.integrity_hash or review.integrity_hash != self._fingerprint(review):
            review.status = "tampered"
            review.decision_reason = "review material changed after submission"
            raise ValueError("review material was tampered with; approval denied")
        normalized = decision.casefold().strip()
        if normalized not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise ValueError("reviewer_id is required")
        review.reviewer_id = reviewer_id.strip()
        review.decision_reason = reason
        if normalized == "approve":
            review.status = "approved"
            review.approval_id = f"HITL-{uuid.uuid4().hex[:8].upper()}"
        else:
            review.status = "rejected"
        return review

    def timeout(self, review_id: str, reason: str = "review timeout") -> HITLReview:
        review = self.reviews[review_id]
        if review.status == "pending":
            review.status = "timeout"
            review.decision_reason = reason
        return review


# ============================================================
# TODO 12: Design 3 HITL decision points + a review lifecycle
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
# - approval_path: What approve/reject/timeout decision is recorded?
# - audit_fields: Which correlation ID, intent and proposed action/diff are logged?
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "High-risk money movement",
        "trigger": "Any transfer_money proposal, regardless of model confidence or claimed authority.",
        "hitl_model": "human-in-the-loop",
        "context_needed": "Verified customer, source/destination accounts, amount, currency, fraud signals, and a before/after diff.",
        "example": "A customer asks the assistant to transfer 50,000,000 VND to a new beneficiary.",
        "approval_path": "Create a pending review; approve only with reviewer identity and approval ID; reject cancels; timeout fails closed and does not send.",
        "audit_fields": "request_id/correlation_id, intent, proposed action, payload diff, risk score, reviewer_id, decision, reason, timestamps, approval_id.",
    },
    {
        "id": 2,
        "name": "Credential/profile change",
        "trigger": "change_password or update_personal_info, or an unusual recovery signal.",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "Identity verification result, previous and proposed values (redacted), device/session risk, and recovery evidence.",
        "example": "A new device requests a phone-number change immediately before a password reset.",
        "approval_path": "Reviewer sees the redacted diff; approve issues a one-time approval; reject locks the proposal; timeout leaves the old profile unchanged.",
        "audit_fields": "request_id/correlation_id, intent, redacted before_after diff, verification factors, reviewer_id, decision, reason, timeout, approval_id.",
    },
    {
        "id": 3,
        "name": "Sensitive external communication",
        "trigger": "Any proposed email/webhook/tool egress containing customer data, internal data, or an untrusted-document instruction.",
        "hitl_model": "human-on-the-loop for low-risk approved templates; human-in-the-loop for new destinations or payloads.",
        "context_needed": "Source provenance, exact destination, allowlist result, redacted payload, data classification, and requested business purpose.",
        "example": "An email attachment asks the agent to send account details to a newly introduced external endpoint.",
        "approval_path": "Unknown destination or sensitive payload is rejected by default; a reviewer may approve only a sanitized, allowlisted payload; reject/timeout means no egress.",
        "audit_fields": "request_id/correlation_id, source, intent, destination, allowlist decision, payload hash/redacted diff, reviewer_id, decision, reason, timestamps.",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
