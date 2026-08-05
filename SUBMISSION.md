# Hướng dẫn nộp bài — Day 11

## Bài tập cá nhân

Bài Day 11 **làm một mình**, gồm 2 hạng mục:

| Hạng mục | Tỷ lệ | Điểm |
|----------|-------|------|
| **A. Tấn công** | 20% | 20 |
| **B. Phòng thủ** | 80% | 80 |
| **Thưởng** (lớp bảo vệ thứ 6) | +10 | Cộng rồi cắt trần 100 |

- Mỗi bài gắn **một MSSV**
- Không nộp repo nhóm, không chia sẻ notebook bài nộp
- Thảo luận ý tưởng được; code và báo cáo phải là của bạn

Đề bài chi tiết: [`assignment11_defense_pipeline.md`](assignment11_defense_pipeline.md).

---

## Hạn nộp

**Thứ sáu 7/8, 23:59 giờ Việt Nam (ICT, UTC+7).**

| Trễ | Phạt |
|-----|------|
| ≤ 24 giờ | Trừ 10% điểm đạt được |
| ≤ 48 giờ | Trừ 25% |
| > 48 giờ | Không nhận bài |

---

## Cách nộp

Chọn **một**:

| Hình thức | Yêu cầu |
|-----------|---------|
| **GitHub** (ưu tiên) | Repo private: `AICB-P1-Assignment11-<MSSV>`. Mời tài khoản giảng viên / bot. Commit nộp trên `main`. |
| **ZIP** (LMS) | `AICB-P1-Assignment11-<MSSV>.zip`, giải nén đúng cấu trúc bên dưới. |

Thay `<MSSV>` bằng mã SV (ví dụ `SE12345`).

---

## Cấu trúc thư mục bắt buộc

```
AICB-P1-Assignment11-<MSSV>/
├── README.md                             # Họ tên, MSSV, cách chạy
├── notebooks/
│   └── <MSSV>_assignment11.ipynb         # Demo A + B (bắt buộc, còn output)
├── src/
│   ├── attacks/                          # Code hạng mục A
│   ├── assignment/                       # Code hạng mục B
│   └── ...                               # guardrails / hitl nếu dùng
├── outputs/
│   ├── attack_results.json               # Kết quả tấn công (A) — bắt buộc
│   ├── results.json                      # Kết quả pipeline phòng thủ (B)
│   ├── audit_log.json
│   └── metrics.json
├── report/
│   └── <MSSV>_report.md                  # Báo cáo (chủ yếu phần B + tóm tắt A)
└── requirements.txt
```

---

## Tên file bắt buộc

| Loại | Tên file |
|------|----------|
| Notebook | `notebooks/<MSSV>_assignment11.ipynb` |
| Báo cáo | `report/<MSSV>_report.md` hoặc `.pdf` |
| Kết quả tấn công | `outputs/attack_results.json` |
| Kết quả phòng thủ | `outputs/results.json` |
| Audit | `outputs/audit_log.json` |
| Metrics | `outputs/metrics.json` |

Notebook phải **còn output đã chạy** cho:

- Phần A: chạy ≥5 attack + (nếu có) attack do AI sinh
- Phần B: Test 1–4 (an toàn / tấn công / rate-limit / edge cases)

Xóa hết output trước khi nộp = bài chưa hoàn chỉnh.

---

## Thang điểm chi tiết

### A. Tấn công — 20 điểm (20%)

| Tiêu chí | Điểm | Kỳ vọng |
|----------|------|---------|
| **5+ prompt tấn công** | 8 | Đủ kỹ thuật nâng cao (completion, translation, creative, confirmation, multi-step…) — không chỉ “ignore all instructions” |
| **Red team bằng AI** | 4 | Dùng LLM sinh thêm ≥5 attack mới, lưu trong bài |
| **Chạy thật + bằng chứng** | 8 | Có `outputs/attack_results.json` và output notebook: agent unsafe có lộ secret / hành vi nguy hiểm được ghi nhận |

Ví dụ tối thiểu `outputs/attack_results.json`:

```json
{
  "student_id": "SE12345",
  "target": "unsafe_vinbank_agent",
  "attacks": [
    {
      "id": 1,
      "category": "Completion",
      "input": "...",
      "response_preview": "...",
      "leaked": true,
      "notes": "Lộ admin123 / API key"
    }
  ],
  "ai_generated_attacks": [
    {"id": 1, "input": "...", "category": "..."}
  ]
}
```

### B. Phòng thủ — 80 điểm (80%)

| Tiêu chí | Điểm | Kỳ vọng |
|----------|------|---------|
| **Pipeline chạy suốt** | 8 | Các lớp khởi tạo được, agent trả lời được |
| **Rate Limiter** | 6 | Test 3: một phần request bị chặn đúng |
| **Input Guardrails** | 10 | Test 2: attack bị chặn ở input (ghi pattern) |
| **Output Guardrails** | 10 | PII/secret bị redact (before/after) |
| **LLM-as-Judge** | 10 | Có điểm đa tiêu chí |
| **Comment code** | 4 | Mỗi hàm/class giải thích làm gì / vì sao cần |
| **Báo cáo (Part B)** | 32 | Trả lời đủ 5 câu hỏi trong đề (xem bảng báo cáo bên dưới) |
| **Tổng B** | **80** | |

#### Báo cáo 32 điểm (nằm trong 80% Phòng thủ)

| # | Nội dung | Điểm |
|---|----------|------|
| 1 | Phân tích lớp chặn 7 attack (bảng) | 8 |
| 2 | False positive / trade-off bảo mật–dễ dùng | 6 |
| 3 | 3 attack vẫn lọt + đề xuất lớp bổ sung | 8 |
| 4 | Sẵn sàng production (latency, cost, monitor) | 6 |
| 5 | Suy nghĩ đạo đức về “an toàn tuyệt đối” | 4 |

### Thưởng +10

Thêm lớp bảo vệ thứ 6 do bạn tự thiết kế.  
Điểm cuối = `min(A + B + thưởng, 100)`.

---

## Định dạng `outputs/results.json` (Phần B)

Khớp [`schemas/results.schema.json`](schemas/results.schema.json). Ví dụ:

```json
{
  "student_id": "SE12345",
  "framework": "google-adk | langgraph | nemo | pure-python | other",
  "safe_queries": [
    {"input": "...", "blocked": false, "layer": null, "response_preview": "..."}
  ],
  "attack_queries": [
    {"input": "...", "blocked": true, "layer": "input_guardrail", "response_preview": "..."}
  ],
  "rate_limit": {
    "max_requests": 10,
    "window_seconds": 60,
    "sent": 15,
    "passed": 10,
    "blocked": 5
  },
  "edge_cases": [
    {"input": "", "blocked": true, "layer": "input_guardrail"}
  ],
  "judge_sample": [
    {
      "response_preview": "...",
      "safety": 5,
      "relevance": 4,
      "accuracy": 4,
      "tone": 5,
      "verdict": "PASS"
    }
  ]
}
```

- `blocked: false` = cho qua; `true` = bị chặn  
- `layer` = lớp chặn (`rate_limiter`, `input_guardrail`, `output_guardrail`, `llm_judge`, …)

---

## Tự kiểm trước khi nộp

```powershell
pip install -r requirements.txt
pytest tests/smoke -q
pytest tests/public -q
python scripts/grade.py --submission-dir . --out outputs/grade_report.json
```

Cần có `outputs/attack_results.json` và `outputs/results.json` trước khi nộp.

Nếu máy không chạy được code (thiếu lib, sai path, lỗi cú pháp): phần chấm máy = **lỗi kỹ thuật** — sửa đóng gói trước. Báo cáo luôn do người chấm.

---

## Trung thực học thuật

- Không commit API key (dùng `.env`)
- Không chia sẻ test ẩn
- Dùng thư viện ngoài thì ghi nguồn trong README / báo cáo
