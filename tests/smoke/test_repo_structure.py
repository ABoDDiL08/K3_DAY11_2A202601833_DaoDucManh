"""Smoke tests — must pass on the starter repo (no API key)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_docs_exist():
    for rel in [
        "README.md",
        "SUBMISSION.md",
        "assignment11_defense_pipeline.md",
        ".env.example",
        "requirements.txt",
        "schemas/results.schema.json",
    ]:
        assert (ROOT / rel).is_file(), f"Missing {rel}"


def test_assignment_starters_exist():
    for rel in [
        "src/assignment/rate_limiter.py",
        "src/assignment/audit_log.py",
        "src/assignment/monitoring.py",
        "src/assignment/pipeline.py",
    ]:
        assert (ROOT / rel).is_file(), f"Missing {rel}"


def test_no_solution_notebook_shipped():
    sol = ROOT / "notebooks" / "lab11_guardrails_hitl_solution.ipynb"
    assert not sol.exists(), "Do not ship solution notebook"


def test_results_schema_is_valid_jsonschema():
    import json
    import jsonschema

    schema = json.loads((ROOT / "schemas" / "results.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
