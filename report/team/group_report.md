# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Tetris.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model: `openai` / `gpt-4o-mini` cho cả v0–v3 (run OpenRouter v0 `v0_B_base_openrouter_20261110T174228887509.json` có `provider_error_cases=20` nên bị loại).

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

- **v1 — `system_prompt.md`:** bỏ chỉ dẫn xấu của starter ("người dùng ghét bị hỏi lại, cứ đoán", "không rõ của ai thì chọn Sam Altman", "bài này thì tự đoán URL"); thay bằng yêu cầu hỏi lại khi thiếu handle/URL.
- **v2 — `system_prompt.md`:** biến việc hỏi lại thành rule bắt buộc: kiểm tra đủ argument trước khi chọn tool, thiếu thì **phải** gọi `clarify`; tóm tắt bài viết cần URL hoặc nội dung, không bịa URL/placeholder (`https://example.com`); chỉ gọi `fetch` khi đã có URL; bỏ câu "luôn xong trong một bước, tự điền args theo phán đoán".
- **v3 — `system_prompt.md`:** thay câu "just go ahead and do it" của starter (gửi ngay, không hỏi) bằng quy ước `response_type` cho `clarify`: `text` khi thiếu thông tin (handle, URL, nội dung), `yes_no` để xác nhận **trước** mọi yêu cầu gửi/đăng (kể cả khi nội dung chưa sẵn sàng), `choice` kèm `options`; chỉ gọi `send` với `confirmed=true` sau khi người dùng đồng ý ở lượt sau. `tools.yaml` giữ declaration như v2.
- **Tool mới `save_note`:** lưu ghi chú nghiên cứu kèm URL nguồn vào file JSON cục bộ; chỉ gọi khi người dùng yêu cầu lưu rõ ràng và đã xác nhận (`confirmed=true`); thiếu tiêu đề/nội dung/URL nguồn thì hỏi lại bằng `clarify`.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa; metric = `summary.case_accuracy` | — | 0.70 (14/20) | [v0_B_base_openai_20261110T174608830282.json](../../starter_v0/runs/v0_B_base_openai_20261110T174608830282.json) |
| v1 | `system_prompt.md` | Chỉ dẫn "đừng hỏi lại, cứ đoán" của starter khiến model bịa handle/URL. Bỏ chỉ dẫn đó, yêu cầu hỏi lại khi thiếu handle/URL để giảm `missing_info` (R10, R11). | 0.70 (14/20) | 0.85 (17/20) | [v1_B_base_openai_20261110T183231184157.json](../../starter_v0/runs/v1_B_base_openai_20261110T183231184157.json) |
| v2 | `system_prompt.md` | Ở v1 model vẫn điền placeholder (`screenname="your_twitter_handle"`, `url="https://example.com"`) vì rule hỏi lại còn mềm và câu "pick one tool… best judgment" còn sót. Thêm rule bắt buộc gọi `clarify` khi thiếu argument, cấm URL placeholder, chỉ `fetch` khi có URL. | 0.85 (17/20) | 0.90 (18/20) | [v2_B_base_openai_20261110T191121924811.json](../../starter_v0/runs/v2_B_base_openai_20261110T191121924811.json) |
| v3 | `system_prompt.md` | Ở v2 model gọi đúng `clarify` nhưng bỏ `response_type` (R11) hoặc xin nội dung thay vì xác nhận gửi (R12), vì prompt không nêu quy ước `response_type` và còn câu "cứ gửi luôn". Thay câu đó bằng quy ước `text` / `yes_no` / `choice` và rule xác nhận trước khi `send`. | 0.90 (18/20) | 1.00 (20/20) | [v3_B_base_openai_20261110T194744125722.json](../../starter_v0/runs/v3_B_base_openai_20261110T194744125722.json) |

**Diễn biến FAIL theo version:** v0 = R08, R10, R11, R12, R13, R14 → v1 = R10, R11, R12 → v2 = R11, R12 (gọi đúng `clarify` nhưng thiếu `response_type`) → v3 = không còn case FAIL.

| Version | case_accuracy | tool_routing | argument | multiturn | prompt_hash | tools_hash |
|---|---:|---:|---:|---:|---|---|
| v0 | 0.70 | 0.75 | 0.70 | 1.00 | `eb1c8179815b` | `e69bc53ed884` |
| v1 | 0.85 | 0.85 | 0.85 | 1.00 | `81475ad40f86` | `e69bc53ed884` |
| v2 | 0.90 | 1.00 | 0.90 | 1.00 | `20301ce71a59` | `e69bc53ed884` |
| v3 | 1.00 | 1.00 | 1.00 | 1.00 | `46fe3af13372` | `b177a8d37d23` |

Mỗi version CP2 chỉ đổi `system_prompt.md` (v1, v2, v3), nên `prompt_hash` khác version trước. `tools_hash` ở v3 đổi từ `e69bc53ed884` sang `b177a8d37d23` vì tool `save_note` (CP3, commit `a6871d0`) được thêm vào `tools.yaml`, không phải giả thuyết CP2, nên hash của artifact đó khác version trước. Cả 4 run đều có `provider_error_cases=0`, `measured_cases=total_cases=20`.

**Ghi chú v3:** R11 → `clarify(response_type="text")`, R12 → `clarify(response_type="yes_no")` ("Bạn có xác nhận muốn gửi bản tin này lên Telegram không?"), R10 cũng truyền `response_type="text"`; M06 gọi đúng `lookup(query="OpenAI", topic="news")`.

**Run đối chứng (tách tác động của `save_note`):** chạy prompt v2 + `tools.yaml` hiện tại (`v2ctl+p20301ce71a59+tb177a8d37d23`, không lưu vào `runs/`) được 0.80 (16/20): FAIL R10, R11 (`response_type` = None), R12 (gọi `send` thẳng), R13 (thiếu `topic="news"`). Như vậy mức tăng lên 1.00 đến từ thay đổi prompt v3, không phải từ việc thêm `save_note`. Run đối chứng cũng cho thấy kết quả `gpt-4o-mini` dao động giữa các lần chạy (R10, R13 PASS ở run v2 chính thức nhưng FAIL ở đối chứng), nên chênh lệch ±1–2 case giữa hai run đơn lẻ chưa đủ kết luận.

**Lần thử bị loại:** trước đó nhóm thử v3 bằng cách chỉ sửa declaration `clarify` trong `tools.yaml` (0.90: sửa R11 nhưng R12 vẫn chọn `"text"`, M06 FAIL); thay bằng hướng sửa prompt ở trên vì cải thiện tốt hơn.

### B2. Failure Analysis

Nguồn: [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T174608830282.json), `results[*].result.failures`, `observed_mismatch`, `actual_tool_calls` và `expect`. Cả 6 case FAIL được phân tích dưới đây. Cột Fix là giả thuyết cho CP2, chưa áp dụng vào baseline.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | `out_of_scope` (`unexpected_tool_call`); đồng thời vượt boundary gửi | `send(text="Nguyên hàm của x^2 là …")` | Mong đợi không gọi tool và từ chối/định hướng vì ngoài phạm vi research; thực tế gọi `send` dù không có yêu cầu gửi hay xác nhận. Tool trả `needs_confirmation`, không phải gửi thành công. | Prompt: quy định phạm vi research, trả lời từ chối/định hướng không dùng tool; không dùng `send` để trả lời hội thoại. |
| R10_missing_handle | `missing_info` (`missing_tool_call`) | `timeline(screenname="sama")` | Thiếu handle nhưng tự đoán `sama`; thiếu `clarify(response_type="text")`, thừa `timeline`. | Prompt: thiếu tài khoản thì hỏi lại bằng `clarify`, không tự chọn người. |
| R11_missing_url | `missing_info` (`missing_tool_call`) | `fetch(url="https://example.com/article")` | Người dùng chưa cung cấp URL nhưng model tự tạo URL; thiếu `clarify(response_type="text")`, thừa `fetch`. | Prompt: yêu cầu URL khi người dùng nói “bài này” mà chưa có link; không bịa URL. |
| R12_confirm_before_send | `wrong_boundary` (`missing_tool_call`) | `send(text="Bản tin này đã được đăng lên Telegram.")` | Thiếu `clarify(response_type="yes_no")` trước hành động gửi; gọi `send` và tạo nội dung tuyên bố đã đăng dù chưa xác nhận. Tool chặn với `needs_confirmation`. | Prompt/tool declaration: hỏi xác nhận trước khi gửi; chỉ gọi `send` với `confirmed=true` sau xác nhận rõ ràng; không tuyên bố thành công trước kết quả tool. |
| R13_parallel_web_and_tweets | `wrong_arg_value` (observed); nhãn case/run: `wrong_tool` | `lookup(query="AI news", timeframe="day", max_results=5)`; `social_search(query="AI", search_type="Latest", limit=5)` | Routing đúng cả hai tool (`routing_correct=true`), nhưng `lookup.query` phải là `"AI"` và thiếu `topic="news"` (tool thực thi mặc định `"general"`). | Tool declaration: tách chủ đề tìm kiếm (`query="AI"`) khỏi loại nội dung (`topic="news"`); giữ `timeframe="day"` khi yêu cầu tin hôm nay. |
| R14_out_of_scope_coding | `out_of_scope` (`unexpected_tool_call`); đồng thời vượt boundary gửi | `send(text="Dưới đây là một hàm Python tính số Fibonacci …")` | Câu hỏi coding ngoài phạm vi research nhưng model viết code rồi gọi `send` để "trả lời"; mong đợi không gọi tool. Cùng pattern với R08. | Prompt/tool declaration: như R08 — không dùng `send` để trả lời hội thoại; câu ngoài phạm vi thì từ chối/định hướng không dùng tool. |

**Phân biệt loại lỗi:** `wrong_tool` là chọn sai/thiếu tool; `wrong_arg_value` là chọn đúng tool nhưng sai/thiếu giá trị argument; `missing_info` là chưa đủ thông tin và phải hỏi lại thay vì đoán; `wrong_boundary` là vượt ranh giới quyền thực hiện, ví dụ gọi gửi trước xác nhận. Nhãn `case_failure_type` mô tả mục tiêu case, không luôn trùng lỗi thực tế: R13 được run gán `wrong_tool`, nhưng `observed_mismatch="wrong_arg_value"`.

**Số đo v0:** `case_accuracy=0.70`, `tool_routing_accuracy=0.75`, `argument_accuracy=0.70`, `multiturn_accuracy=1.00`. Run hợp lệ để so sánh routing/arguments: `provider_error_cases=0`, `measured_cases=total_cases=20`. Lỗi model provider làm case không đo được nên run có lỗi provider không được dùng làm bằng chứng cải thiện.

**Giới hạn bằng chứng:** Không đồng nhất pass eval với tool thực thi thành công. Run có lỗi HTTP 403 từ RapidAPI Twitter ở 9 case (`timeline`: R01, R05, R10, M01, M03, M05; `social_search`: R02, R07, R13); đây không phải lỗi model provider. `send` trong R08/R12 đã bị guardrail chặn. Cần xử lý quyền truy cập/quota riêng trước khi chứng minh luồng lấy dữ liệu hoạt động end-to-end.

**Tự kiểm tra CP1:** `.venv/bin/python scripts/preflight_provider.py --provider openai --model gpt-4o-mini` pass (`timeline`, `screenname="sama"`, `limit=1`); dùng provider thật của run thay vì ví dụ `openrouter`. `.venv/bin/python -m pytest`: **62 passed, 17 skipped**, 0 failed; các test TODO CP3 còn skipped đúng yêu cầu. Run v0 dùng `prompt_hash=eb1c8179815b…`, `tools_hash=e69bc53ed884…` (artifact starter chưa sửa); run v0 ban đầu `v0_B_base_openai_20261110T173129593859.json` (0.75) đã được chạy lại thành run hiện tại (0.70) ở commit `1e943bd`, nên mọi số liệu trong báo cáo dùng run hiện tại.

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

- **Fix nào thuộc `system_prompt.md`?** Hành vi chung, áp dụng cho mọi tool: không đoán khi thiếu thông tin, bắt buộc hỏi lại trước khi gọi tool (v1, v2 sửa R10, R11 lần đầu). Câu "cứ gửi luôn" của starter cũng thuộc prompt và đã được thay ở v3 bằng quy ước `response_type` + xác nhận trước khi gửi.
- **Fix nào thuộc `tools.yaml`?** Quy ước gắn với một tool cụ thể: giá trị argument (`response_type` của `clarify`) và ranh giới xác nhận của `send` (v3 sửa R11, R12). Lần thử chỉ sửa declaration `clarify` sửa được R11 nhưng không sửa được R12, vì câu "cứ gửi luôn" trong prompt vẫn còn — chỉ dẫn xấu trong prompt phải sửa ở prompt. Khai báo `send` (ranh giới `confirmed`) vẫn là việc nên làm ở `tools.yaml` để guardrail không chỉ dựa vào prompt.
- **Failure nào cần review thủ công?** `no_tool` case (R08, R09, R14) chỉ kiểm tra không gọi tool, không chấm nội dung trả lời có từ chối đúng hay không; R12 kể cả khi PASS cũng chỉ chứng minh có hỏi `yes_no`, không chứng minh lượt sau gửi đúng `confirmed=true`; Kết quả 1.00 của v3 là một lần chạy; vì model dao động (xem run đối chứng) nên cần chạy lại vài lần trước khi coi là ổn định.
- **Nếu có thêm một vòng:** v4 viết lại declaration của `send` trong `tools.yaml` (hành động ghi, chỉ `confirmed=true` sau `yes_no`) và các tool còn mô tả một dòng (`timeline`, `social_search`, `lookup`: quy ước handle, `topic=news`, `search_type=Top`), rồi chạy v3/v4 mỗi bản 3 lần để đo độ ổn định. Kiểm tra thêm bằng `--suite group` vì base suite đã bão hòa ở 20/20.

## 8. Tài liệu tham khảo

-
