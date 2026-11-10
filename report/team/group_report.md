# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Tetris.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model baseline v0: `openai` / `gpt-4o-mini`; v1–v3 chưa chạy.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa; metric = `summary.case_accuracy` | — | 0.75 (15/20) | [v0_B_base_openai_20261110T173129593859.json](../../starter_v0/runs/v0_B_base_openai_20261110T173129593859.json) |
| v1 | `system_prompt.md` | Loại bỏ chỉ dẫn tự suy đoán thông tin còn thiếu, yêu cầu hỏi lại khi thiếu account handle hoặc URL bắt buộc để giảm lỗi `missing_info`. | 0.75 (15/20) | 0.85 (17/20) | [v1_B_base_openai_20261110T183231184157.json](../../starter_v0/runs/v1_B_base_openai_20261110T183231184157.json) |
| v2 | `system_prompt.md` | Loại bỏ cơ chế tự suy đoán thông tin khi thiếu account handle hoặc URL để giảm lỗi missing_info | 0.85 (17/20) | 0.90 (18/20) |(../../starter_v0/runs/v2_B_base_openai_20261110T191121924811.json) |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Nguồn: [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T173129593859.json), `results[*].result.failures`, `observed_mismatch`, `actual_tool_calls` và `expect`. Cả 5 case FAIL được phân tích dưới đây. Cột Fix là giả thuyết cho CP2, chưa áp dụng vào baseline.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | `out_of_scope` (`unexpected_tool_call`); đồng thời vượt boundary gửi | `send(text="Nguyên hàm của x^2 là …")` | Mong đợi không gọi tool và từ chối/định hướng vì ngoài phạm vi research; thực tế gọi `send` dù không có yêu cầu gửi hay xác nhận. Tool trả `needs_confirmation`, không phải gửi thành công. | Prompt: quy định phạm vi research, trả lời từ chối/định hướng không dùng tool; không dùng `send` để trả lời hội thoại. |
| R10_missing_handle | `missing_info` (`missing_tool_call`) | `timeline(screenname="sama")` | Thiếu handle nhưng tự đoán `sama`; thiếu `clarify(response_type="text")`, thừa `timeline`. | Prompt: thiếu tài khoản thì hỏi lại bằng `clarify`, không tự chọn người. |
| R11_missing_url | `missing_info` (`missing_tool_call`) | `fetch(url="https://example.com/article")` | Người dùng chưa cung cấp URL nhưng model tự tạo URL; thiếu `clarify(response_type="text")`, thừa `fetch`. | Prompt: yêu cầu URL khi người dùng nói “bài này” mà chưa có link; không bịa URL. |
| R12_confirm_before_send | `wrong_boundary` (`missing_tool_call`) | `send(text="Bản tin này đã được đăng lên Telegram.")` | Thiếu `clarify(response_type="yes_no")` trước hành động gửi; gọi `send` và tạo nội dung tuyên bố đã đăng dù chưa xác nhận. Tool chặn với `needs_confirmation`. | Prompt/tool declaration: hỏi xác nhận trước khi gửi; chỉ gọi `send` với `confirmed=true` sau xác nhận rõ ràng; không tuyên bố thành công trước kết quả tool. |
| R13_parallel_web_and_tweets | `wrong_arg_value` (observed); nhãn case/run: `wrong_tool` | `lookup(query="AI news", timeframe="day", max_results=5)`; `social_search(query="AI", search_type="Latest", limit=5)` | Routing đúng cả hai tool (`routing_correct=true`), nhưng `lookup.query` phải là `"AI"` và thiếu `topic="news"` (tool thực thi mặc định `"general"`). | Tool declaration: tách chủ đề tìm kiếm (`query="AI"`) khỏi loại nội dung (`topic="news"`); giữ `timeframe="day"` khi yêu cầu tin hôm nay. |

**Phân biệt loại lỗi:** `wrong_tool` là chọn sai/thiếu tool; `wrong_arg_value` là chọn đúng tool nhưng sai/thiếu giá trị argument; `missing_info` là chưa đủ thông tin và phải hỏi lại thay vì đoán; `wrong_boundary` là vượt ranh giới quyền thực hiện, ví dụ gọi gửi trước xác nhận. Nhãn `case_failure_type` mô tả mục tiêu case, không luôn trùng lỗi thực tế: R13 được run gán `wrong_tool`, nhưng `observed_mismatch="wrong_arg_value"`.

**Số đo v0:** `case_accuracy=0.75`, `tool_routing_accuracy=0.80`, `argument_accuracy=0.75`, `multiturn_accuracy=1.00`. Run hợp lệ để so sánh routing/arguments: `provider_error_cases=0`, `measured_cases=total_cases=20`. Lỗi model provider làm case không đo được nên run có lỗi provider không được dùng làm bằng chứng cải thiện.

**Giới hạn bằng chứng:** Không đồng nhất pass eval với tool thực thi thành công. Run có lỗi HTTP của dịch vụ tool, ví dụ R01 `timeline` trả 403, R10 trả 429 và R13 `social_search` trả 403; đây không phải lỗi model provider. `send` trong R08/R12 đã bị guardrail chặn. Cần xử lý quyền truy cập/quota riêng trước khi chứng minh luồng lấy dữ liệu hoạt động end-to-end.

**Tự kiểm tra CP1:** `.venv/bin/python scripts/preflight_provider.py --provider openai --model gpt-4o-mini` pass (`timeline`, `screenname="sama"`, `limit=1`); dùng provider thật của run thay vì ví dụ `openrouter`. `.venv/bin/python -m pytest`: **62 passed, 17 skipped**, 0 failed; các test TODO CP3 còn skipped đúng yêu cầu. SHA-256 của `artifacts/system_prompt.md` và `artifacts/tools.yaml` hiện tại trùng `prompt_hash`/`tools_hash` trong run v0; không sửa hai artifact trong bước hoàn thiện CP1.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
