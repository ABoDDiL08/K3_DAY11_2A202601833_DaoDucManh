# Day-11-Guardrails-HITL-Responsible-AI

Day 11 — Guardrails, HITL & Responsible AI: How to make agent applications safe?

## Objectives

- Understand why guardrails are mandatory for AI products
- Implement input guardrails (injection detection, topic filter)
- Implement output guardrails (content filter, LLM-as-Judge)
- Use NeMo Guardrails (NVIDIA) with Colang
- Design HITL workflow with confidence-based routing
- Perform basic red teaming

## Scenario

You secure a **VinBank** customer-service chatbot.

The **unsafe agent** intentionally embeds secrets in its system prompt (`admin123`, `sk-vinbank-secret-2024`, internal DB host) so you can:

1. Attack it and observe leaks
2. Add guardrails
3. Measure improvement
4. Design human escalation (HITL)

Defense flow:

```
User Input → Input Guardrails → LLM → Output Guardrails → Response
                 ↑                            ↑
          injection / topic            PII / secrets / Judge
```

## Project Structure

```
Day-11-Guardrails-HITL-Responsible-AI/
├── notebooks/
│   ├── lab11_guardrails_hitl.ipynb            # Student lab (Colab)
│   ├── attack_defense_arena.ipynb             # Optional attack/defense playground
│   └── lab11_guardrails_hitl_solution.ipynb   # Solution (instructor only)
├── src/                                       # Local Python version
│   ├── main.py                    # Entry point — run all parts or pick one
│   ├── core/
│   │   ├── config.py              # API key setup, allowed/blocked topics
│   │   └── utils.py               # chat_with_agent() helper
│   ├── agents/
│   │   └── agent.py               # Unsafe & protected agent creation
│   ├── attacks/
│   │   └── attacks.py             # TODO 1-2: Adversarial prompts & AI red teaming
│   ├── guardrails/
│   │   ├── input_guardrails.py    # TODO 3-5: Injection detection, topic filter, plugin
│   │   ├── output_guardrails.py   # TODO 6-8: Content filter, LLM-as-Judge, plugin
│   │   └── nemo_guardrails.py     # TODO 9: NeMo Guardrails with Colang
│   ├── testing/
│   │   └── testing.py             # TODO 10-11: Before/after comparison, pipeline
│   └── hitl/
│       └── hitl.py                # TODO 12-13: Confidence router, HITL design
├── assignment11_defense_pipeline.md           # Post-lab assignment
├── Slide_Lab_Day11.html                       # Lab slide deck (timers per part)
├── requirements.txt
└── README.md
```

## Setup

### Google Colab (recommended)

1. Upload `notebooks/lab11_guardrails_hitl.ipynb` to Google Colab
2. Create a Google API Key at [Google AI Studio](https://aistudio.google.com/apikey)
3. Save the API key in Colab Secrets as `GOOGLE_API_KEY`
4. Run cells in order

### Local (Notebook)

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY="your-api-key-here"   # Windows PowerShell: $env:GOOGLE_API_KEY="..."
jupyter notebook notebooks/lab11_guardrails_hitl.ipynb
```

### Local (Python modules — no Colab needed)

```bash
cd src/
pip install -r ../requirements.txt
export GOOGLE_API_KEY="your-api-key-here"   # Windows PowerShell: $env:GOOGLE_API_KEY="..."

# Run the full lab
python main.py

# Or run specific parts
python main.py --part 1    # Part 1: Attacks
python main.py --part 2    # Part 2: Guardrails
python main.py --part 3    # Part 3: Testing pipeline
python main.py --part 4    # Part 4: HITL design

# Or test individual modules
python guardrails/input_guardrails.py
python guardrails/output_guardrails.py
python testing/testing.py
python hitl/hitl.py
```

### Tools Used

- **Google ADK** — Agent Development Kit (plugins, runners)
- **NeMo Guardrails** — NVIDIA framework with Colang (declarative safety rules)
- **Gemini 2.5 Flash/Flash Lite** — LLM backend (you can switch to other models if you want)

---

## Timeline (2.5 hours)

| Time | Part | Content | TODOs | Duration |
|------|------|---------|-------|----------|
| 0:00 – 0:30 | Part 1 | Attack unprotected agent + AI red teaming | TODO 1–2 | 30 min |
| 0:30 – 0:50 | Part 2A | Implement input guardrails (injection detection, topic filter, ADK plugin) | TODO 3–5 | 20 min |
| 0:50 – 1:10 | Part 2B | Implement output guardrails (content filter, LLM-as-Judge, ADK plugin) | TODO 6–8 | 20 min |
| 1:10 – 1:30 | Part 2C | NeMo Guardrails with Colang (NVIDIA) | TODO 9 | 20 min |
| *(optional)* | Break | Suggested short break — not counted in the 150 min | — | ~10 min |
| 1:30 – 2:00 | Part 3 | Before/after comparison + automated testing pipeline | TODO 10–11 | 30 min |
| 2:00 – 2:30 | Part 4 | Design HITL workflow (confidence router + decision points) | TODO 12–13 | 30 min |

Slide deck with per-part timers: `Slide_Lab_Day11.html`.

**After the lab — Assignment 11:** build a production defense-in-depth pipeline (≥4 independent safety layers + audit/monitoring) and submit a `.ipynb` + individual report (see `assignment11_defense_pipeline.md`). Due: **end of Week 11**.

---

## What You Need To Do (step by step)

Complete the **13 TODOs** in order. After each part, run the matching command to verify.

### Part 1 — Attack the unprotected agent (TODO 1–2) · ~30 min

**File:** `src/attacks/attacks.py` (or the matching notebook cells)

| TODO | What to implement |
|------|-------------------|
| **1** | Replace the 5 `"TODO: ..."` strings in `adversarial_prompts` with real attack prompts. Simple `"Ignore all instructions"` is often refused — use stronger techniques: **Completion**, **Translation/Reformatting**, **Hypothetical/Creative**, **Confirmation/Side-channel**, **Multi-step escalation** (hints are in the file). |
| **2** | Write a red-team prompt for Gemini that generates **5 additional** creative attacks. Describe the target (VinBank chatbot) and that basic injection already fails. |

**Verify:** `python main.py --part 1`

**Goal:** Observe secret leaks or unsafe answers from the unprotected agent. Save the results — you will reuse them in the Security Report.

---

### Part 2A — Input guardrails (TODO 3–5) · ~20 min

**File:** `src/guardrails/input_guardrails.py`

| TODO | What to implement |
|------|-------------------|
| **3** | Fill ≥5 regex patterns into `INJECTION_PATTERNS` inside `detect_injection()` (e.g. ignore previous instructions, you are now, system prompt, reveal your prompt, pretend you are). |
| **4** | Implement `topic_filter()`: block if input matches a **blocked** topic; block if it matches **no allowed** topic; otherwise allow. Topic lists live in `core/config.py`. |
| **5** | In `InputGuardrailPlugin.on_user_message_callback`: call injection check → topic filter; if bad, `return self._block_response(...)`; if OK, `return None` (pass through). |

**Verify:** `python guardrails/input_guardrails.py` or `python main.py --part 2`

---

### Part 2B — Output guardrails (TODO 6–8) · ~20 min

**File:** `src/guardrails/output_guardrails.py`

| TODO | What to implement |
|------|-------------------|
| **6** | Fill `PII_PATTERNS` with regex for VN phone, email, CMND/CCCD, API keys (`sk-...`), password patterns. The function already redacts matches as `[REDACTED]`. |
| **7** | Create `safety_judge_agent` with `LlmAgent` using `SAFETY_JUDGE_INSTRUCTION`. Do **not** put `{placeholders}` in the instruction (ADK treats them as template variables). |
| **8** | In `OutputGuardrailPlugin.after_model_callback`: run `content_filter` (redact) + optional `llm_safety_check`; if UNSAFE, replace the response with a safe message. |

**Verify:** `python guardrails/output_guardrails.py`

---

### Part 2C — NeMo Guardrails (TODO 9) · ~20 min

**File:** `src/guardrails/nemo_guardrails.py`

| TODO | What to implement |
|------|-------------------|
| **9** | Add ≥3 new Colang rules beyond the provided ones: **Role confusion** (e.g. DAN), **Encoding attacks** (Base64/ROT13), **Vietnamese injection**. Each rule needs `define user` + `define bot` + `define flow`. Add matching test messages. |

Requires: `pip install nemoguardrails` (Part 2C is skipped if missing).

**Verify:** included in `python main.py --part 2`

---

### Part 3 — Measure effectiveness (TODO 10–11) · ~30 min

**File:** `src/testing/testing.py`

| TODO | What to implement |
|------|-------------------|
| **10** | Create `InputGuardrailPlugin` + `OutputGuardrailPlugin`, pass them to `create_protected_agent(plugins=...)`, rerun the same 5 attacks from TODO 1, and compare unprotected vs protected. |
| **11** | Implement `SecurityTestPipeline`: run a batch of attacks → classify blocked/leaked → compute block rate / leak rate → print a report. |

This part is the main source for **Deliverable 1 (Security Report)**.

**Verify:** `python main.py --part 3`

---

### Part 4 — HITL design (TODO 12–13) · ~30 min

**File:** `src/hitl/hitl.py`

| TODO | What to implement |
|------|-------------------|
| **12** | Implement `ConfidenceRouter.route()`: high-risk actions always escalate; confidence ≥ 0.9 → auto-send; 0.7–0.9 → queue for review; &lt; 0.7 → escalate. |
| **13** | Fill 3 banking decision points (`name`, `trigger`, `hitl_model`, `context_needed`, `example`) — e.g. large transfer, account closure, password change. |

This part is the main source for **Deliverable 2 (HITL Flowchart)**.

**Verify:** `python main.py --part 4`

---

## 13 TODOs (summary)

| # | Description | File | Framework |
|---|-------------|------|-----------|
| 1 | Write 5 adversarial prompts | `attacks/attacks.py` | — |
| 2 | Generate attack test cases with AI | `attacks/attacks.py` | Gemini |
| 3 | Injection detection (regex) | `guardrails/input_guardrails.py` | Python |
| 4 | Topic filter | `guardrails/input_guardrails.py` | Python |
| 5 | Input Guardrail Plugin | `guardrails/input_guardrails.py` | Google ADK |
| 6 | Content filter (PII, secrets) | `guardrails/output_guardrails.py` | Python |
| 7 | LLM-as-Judge safety check | `guardrails/output_guardrails.py` | Gemini |
| 8 | Output Guardrail Plugin | `guardrails/output_guardrails.py` | Google ADK |
| 9 | NeMo Guardrails Colang config | `guardrails/nemo_guardrails.py` | NeMo |
| 10 | Rerun 5 attacks with guardrails | `testing/testing.py` | Google ADK |
| 11 | Automated security testing pipeline | `testing/testing.py` | Python |
| 12 | Confidence Router (HITL) | `hitl/hitl.py` | Python |
| 13 | Design 3 HITL decision points | `hitl/hitl.py` | Design |

---

## Deliverables

1. **Security Report** — Before/after comparison of **5+ attacks** (unprotected vs ADK guardrails; include NeMo if available). Note which attacks were blocked vs still leaked.
2. **HITL Flowchart** — **3 decision points** with escalation paths (derived from TODO 13).

---

## Completion checklist

```
[ ] TODO 1–2   attacks.py            — 5 prompts + AI red team
[ ] TODO 3–5   input_guardrails.py   — regex + topic + plugin
[ ] TODO 6–8   output_guardrails.py  — PII + judge + plugin
[ ] TODO 9     nemo_guardrails.py    — ≥3 Colang rules
[ ] TODO 10–11 testing.py            — before/after + pipeline
[ ] TODO 12–13 hitl.py               — router + 3 decision points
[ ] Security Report (before/after table)
[ ] HITL Flowchart (3 escalation paths)
```

---

## Assignment 11 (after the lab)

See `assignment11_defense_pipeline.md`.

Build a **defense-in-depth production pipeline** with at least:

- Rate Limiter
- Input Guardrails
- Output Guardrails + LLM-as-Judge
- Audit Log + Monitoring / Alerts

Run the required test suites (safe queries, attacks, rate limiting, edge cases). Submit a notebook + a 1–2 page individual report. Framework choice is free (ADK, LangGraph, NeMo, pure Python, etc.). Due: **end of Week 11**.

---

## References

- [OWASP Top 10 for LLM](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Official Google's Gemini cookbook](https://github.com/google-gemini/cookbook/blob/main/examples/gemini_google_adk_model_guardrails.ipynb)
- [AI Safety Fundamentals](https://aisafetyfundamentals.com/)
- [AI Red Teaming Guide](https://github.com/requie/AI-Red-Teaming-Guide)
- [antoan.ai - AI Safety Vietnam](https://antoan.ai)
