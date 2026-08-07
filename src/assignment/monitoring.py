"""
Assignment 11 — Monitoring & Alerts starter (TODO).

Tracks block rate, rate-limit hits, judge fail rate.
Fires alerts when thresholds are exceeded.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Alert:
    metric: str
    value: float
    threshold: float
    message: str


@dataclass
class MonitoringAlert:
    """Aggregate counters from pipeline plugins and emit alerts."""

    block_rate_threshold: float = 0.5
    rate_limit_hit_threshold: int = 5
    judge_fail_rate_threshold: float = 0.3
    alerts: list[Alert] = field(default_factory=list)

    # Counters — update these from your pipeline after each request
    total_requests: int = 0
    blocked_requests: int = 0
    rate_limit_hits: int = 0
    judge_checks: int = 0
    judge_fails: int = 0

    def check_metrics(self) -> list[Alert]:
        """Compute current rates and refresh threshold alerts.

        Checks are idempotent: repeated snapshots update the existing metric
        alert instead of growing duplicate entries forever.
        """
        block_rate = (
            self.blocked_requests / self.total_requests
            if self.total_requests else 0.0
        )
        judge_fail_rate = (
            self.judge_fails / self.judge_checks
            if self.judge_checks else 0.0
        )
        current: dict[str, Alert] = {}
        if self.total_requests and block_rate >= self.block_rate_threshold:
            current["block_rate"] = Alert(
                "block_rate", block_rate, self.block_rate_threshold,
                f"Block rate {block_rate:.1%} reached threshold {self.block_rate_threshold:.1%}",
            )
        if self.rate_limit_hits >= self.rate_limit_hit_threshold:
            current["rate_limit_hits"] = Alert(
                "rate_limit_hits", float(self.rate_limit_hits), float(self.rate_limit_hit_threshold),
                f"Rate-limit hits {self.rate_limit_hits} reached threshold {self.rate_limit_hit_threshold}",
            )
        if self.judge_checks and judge_fail_rate >= self.judge_fail_rate_threshold:
            current["judge_fail_rate"] = Alert(
                "judge_fail_rate", judge_fail_rate, self.judge_fail_rate_threshold,
                f"Judge failure rate {judge_fail_rate:.1%} reached threshold {self.judge_fail_rate_threshold:.1%}",
            )
        self.alerts = list(current.values())
        return self.alerts

    def export_json(self, filepath: str = "outputs/metrics.json"):
        """Write counters, rates and active alerts as JSON."""
        import json
        from pathlib import Path

        self.check_metrics()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.snapshot(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def snapshot(self) -> dict:
        block_rate = (
            self.blocked_requests / self.total_requests
            if self.total_requests
            else 0.0
        )
        judge_fail_rate = (
            self.judge_fails / self.judge_checks if self.judge_checks else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "block_rate": block_rate,
            "rate_limit_hits": self.rate_limit_hits,
            "judge_checks": self.judge_checks,
            "judge_fails": self.judge_fails,
            "judge_fail_rate": judge_fail_rate,
            "alerts": [
                {
                    "metric": a.metric,
                    "value": a.value,
                    "threshold": a.threshold,
                    "message": a.message,
                }
                for a in self.alerts
            ],
        }
