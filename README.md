# Day 11 — Guardrails, HITL & Responsible AI

Làm sao để ứng dụng agent an toàn hơn?

**Hình thức:** bài tập **cá nhân** (1 người / 1 MSSV).

---

## Hai hạng mục cần làm

| Hạng mục | Tỷ lệ | Bạn làm gì |
|----------|-------|------------|
| **A. Tấn công** | **20%** | Viết prompt tấn công agent, red team bằng AI, ghi nhận kết quả |
| **B. Phòng thủ** | **80%** | Xây pipeline bảo vệ nhiều lớp + báo cáo |

Điểm thưởng (tùy chọn): thêm lớp bảo vệ thứ 6 — tối đa **+10** (điểm cuối không vượt 100).

**Hạn nộp:** Chủ nhật tuần 11, **23:59 giờ Việt Nam (ICT)**.

| Tài liệu | Dùng để |
|----------|---------|
| [`assignment11_defense_pipeline.md`](assignment11_defense_pipeline.md) | Đề bài chi tiết (A + B) |
| [`SUBMISSION.md`](SUBMISSION.md) | Cách nộp, tên file, cấu trúc thư mục |

---

## Tình huống

Chatbot ngân hàng **VinBank**. Agent “unsafe” cố ý chứa mật khẩu / API key trong system prompt.

Bạn sẽ:

1. **Tấn công** agent để thấy rủi ro (20%)
2. **Phòng thủ** bằng pipeline nhiều lớp (80%)

```
Câu hỏi người dùng
    → Rate Limiter
    → Lọc đầu vào (Input Guardrails)
    → LLM trả lời
    → Lọc đầu ra (Output Guardrails + Judge)
    → Audit / Monitoring
    → Phản hồi
```

---

## Làm bài trên máy

### Cài đặt

```powershell
Copy-Item .env.example .env
# Mở .env, dán GOOGLE_API_KEY
pip install -r requirements.txt
```

Lấy key: [Google AI Studio](https://aistudio.google.com/apikey)

### Thứ tự làm việc đề xuất

1. **Hạng mục A — Tấn công (20%)**
   - Làm trong `src/attacks/attacks.py` (hoặc notebook)
   - Viết ≥5 prompt tấn công nâng cao + sinh thêm attack bằng AI
   - Chạy tấn agent unsafe, lưu `outputs/attack_results.json`
2. **Hạng mục B — Phòng thủ (80%)**
   - Làm trong `src/assignment/` (+ dùng lại `src/guardrails/`, `src/hitl/` nếu muốn)
   - Chạy Test 1–4, xuất `results.json`, `audit_log.json`, `metrics.json`
   - Viết báo cáo `report/<MSSV>_report.md`
3. Tự kiểm → nộp theo [`SUBMISSION.md`](SUBMISSION.md)

```powershell
cd src
python main.py --part 1          # hỗ trợ phần Tấn công
pytest ../tests/smoke -q
pytest ../tests/public -q
python ../scripts/grade.py --submission-dir .. --out ../outputs/grade_report.json
```

Colab / Jupyter (tuỳ chọn): `notebooks/lab11_guardrails_hitl.ipynb`  
Local là đủ, không bắt buộc Colab.

---

## Cấu trúc repo

```
├── assignment11_defense_pipeline.md   ← Đề bài A + B
├── SUBMISSION.md                      ← Quy định nộp
├── src/
│   ├── attacks/                       ← Hạng mục A (Tấn công)
│   ├── assignment/                    ← Hạng mục B (Phòng thủ) — starters
│   ├── guardrails/ testing/ hitl/     ← Module hỗ trợ phòng thủ
│   └── main.py
├── notebooks/lab11_guardrails_hitl.ipynb
├── schemas/results.schema.json
├── scripts/grade.py
├── tests/
├── Slide_Lab_Day11.html
└── .env.example
```

---

## Tài liệu tham khảo

- [OWASP Top 10 for LLM](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [Google ADK](https://google.github.io/adk-docs/)
- [AI Safety Fundamentals](https://aisafetyfundamentals.com/)
