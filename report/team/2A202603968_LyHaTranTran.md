# Báo cáo cá nhân — LyHaTranTran-2A202603968

## 1. Thông tin thành viên

- Họ tên: Lý Hà Trân Trân
- MSSV: 2A202603968
- Email: 26ai.tranlht@vinuni.edu.vn
- GitHub: TranHa161

## 2. Phần việc phụ trách

- CP2 — **v3** (`system_prompt.md`): phân tích các case còn FAIL ở v2, đặt giả thuyết H3, sửa prompt, chạy base eval v3 và ghi `version_log.csv`.
- CP2 — **v4** (`tools.yaml`): viết lại tool declaration theo yêu cầu C2 (khi nào dùng/không dùng, convention args, boundary xác nhận), chạy base + group eval v4.
- CP5 — transcript live chat v4 và hoàn thiện các mục còn trống của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- **Giả thuyết H3 (v3):** ở [run v2](../../starter_v0/runs/v2_B_base_openai_20261110T191121924811.json) model gọi đúng `clarify` nhưng bỏ `response_type` (R11) hoặc hỏi nội dung thay vì xác nhận gửi (R12). Nguyên nhân: prompt không nêu quy ước `response_type` và còn câu starter "just go ahead and do it". Mình thay câu đó bằng quy ước `text` / `yes_no` / `choice` và rule "chỉ `send(confirmed=true)` sau khi user đồng ý ở lượt sau".
- **Kết quả v3:** base 0.90 → **1.00 (20/20)**, `provider_error_cases=0` ([run v3](../../starter_v0/runs/v3_B_base_openai_20261110T194744125722.json)).
- **Run đối chứng:** chạy prompt v2 + `tools.yaml` có `save_note` (0.80) để tách tác động của tool mới khỏi thay đổi prompt v3. Run này cũng cho thấy `gpt-4o-mini` dao động giữa các lần chạy (ghi ở B1).
- **Chuẩn hoá `version_log.csv`:** sửa dòng v0 về đúng run và hash hợp lệ (`v0_B_base_openai_20261110T174608830282.json`, 0.70), ghi hash SHA-256 đầy đủ cho v1/v2, thêm dòng v3.
- **Group report (commit `0cf7acc`):** viết lại bảng B1 (giả thuyết từng version, bảng metric + hash, diễn biến FAIL, run đối chứng, lần thử bị loại), cập nhật B2 (thêm R14, số liệu v0 mới) và B6 Reflection.
- **v4 — `tools.yaml` (prompt giữ v3):** viết lại description của 11 tool, không đổi tên, tham số, enum hay required. Base giữ **1.00**, group **0.50 → 0.80** (sửa G01, G03, GM04). Ghi dòng v4 vào `version_log.csv`, thêm `.gitattributes` để `tools_hash` không đổi theo line ending.
- **Transcript v4** 5 lượt: yêu cầu thường → thiếu URL rồi bổ sung → yêu cầu gửi Telegram có `clarify(yes_no)` → `send(confirmed=true)`.
- **Hoàn thiện group report:** A1–A3, B1 (v4), B3 (thêm cột v4), B4, B5a, B5, mục 5, 7, 8.

## 4. Bằng chứng

- File/commit/PR:
  - Commit `0cf7acc` ("upgrade v3"): `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/v3_B_base_openai_20261110T194744125722.json`, `report/team/group_report.md`.
  - v4: `starter_v0/artifacts/tools.yaml`, `starter_v0/runs/v4_B_base_openai_20261111T014227776599.json` (1.00), `starter_v0/runs/v4_B_group_openai_20261111T014254803430.json` (0.80), dòng v4 trong `version_log.csv`, `.gitattributes`.
  - Transcript: `starter_v0/transcripts/v4_openai_20261111T014329378074.transcript.json`.
  - Kiểm tra: `cd starter_v0 && python -m pytest` → 92 passed, 0 failed, 0 skipped; `tests/test_tool_contract.py` xanh sau khi đổi `tools.yaml`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude Code để rà repo theo rubric, soạn lại description `tools.yaml` và điền báo cáo. Mọi số liệu trong báo cáo được đọc lại từ `summary` và `results[*].result` của run JSON thật, không chép từ output của AI.
  - Kiểm tra mỗi run có `provider_error_cases == 0` và `measured_cases == total_cases`; so `prompt_hash`/`tools_hash` trong run với `version_log.csv` để chắc mỗi version chỉ đổi một artifact (v3 đổi prompt, v4 đổi tools).

## 5. Tự đánh giá

- Mỗi version chỉ một giả thuyết, một artifact: v3 sửa prompt, v4 sửa declaration. Mỗi version đều có run hợp lệ và metric trước/sau.
- Hiểu ranh giới: hành vi chung (không đoán, xác nhận trước khi gửi) thuộc prompt; quy ước args và khi nào dùng từng tool thuộc `tools.yaml`. Kết quả v4 cho thấy G01, G03, GM04 sửa được chỉ bằng declaration.
- Hạn chế: kết quả là một lần chạy cho mỗi version, mà model có dao động. G04, G05 vẫn FAIL ở v4. Chưa cấu hình Telegram nên `send` chưa gửi thật (`RuntimeError`).
