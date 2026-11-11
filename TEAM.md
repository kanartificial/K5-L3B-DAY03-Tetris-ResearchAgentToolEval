# Team

## Thông tin nhóm

- Tên nhóm: Tetris
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Tetris-ResearchAgentToolEval`
- URL repo: https://github.com/kanartificial/K5-L3B-DAY03-Tetris-ResearchAgentToolEval
- Nhánh nộp, commit chốt: chưa chốt.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Lý Hà Trân Trân | 2A202603968 | 26ai.tranlht@vinuni.edu.vn | TranHa161 | Prompt/tool declaration v3–v4, eval, báo cáo |
|   2 | Vương Thu Thảo | 2A202603966 |26ai.thaovt@vinuni.edu.vn | ThuThaoVuong | Frontend |
|   3 | Khổng Ngọc Anh | 2A202603974 | 26ai.anhkn2@vinuni.edu.vn | kanartificial (commit: kana) | Baseline CP1, tool `save_note`, unit tests, hỗ trợ demo |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## KhongNgocAnh-2A202603974

### Phần việc phụ trách

- CP1: chạy baseline OpenAI, ghi version log và phân tích các case lỗi ban đầu.
- CP3: xây dựng, đăng ký và viết tài liệu cho tool mới `save_note`; hoàn thành các unit test còn skipped.
- Hỗ trợ CP5: thử chat live, lưu transcript và ghi chú mẫu; bổ sung hướng dẫn Cloudflare Tunnel.

### Đóng góp cụ thể

- Baseline trong commit `4922ead`: OpenAI / `gpt-4o-mini`, 15/20 case pass; phân tích 5 case lỗi trong commit `958065b`. Đây là run lịch sử, không phải baseline 0.70 đang được dùng trong `version_log.csv` hiện tại.
- Thêm `save_note`: lưu tiêu đề, nội dung và URL nguồn thành JSON cục bộ; yêu cầu xác nhận, kiểm tra dữ liệu rỗng và trả error dict khi ghi thất bại; đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`, kèm `TOOL.md`.
- Thay 14 test skipped của tool có sẵn bằng kiểm tra offline; thêm 3 test `save_note` với paper *Attention Is All You Need*, bao gồm lưu thành công, nội dung rỗng và lỗi lưu trữ.
- Lưu transcript thử `save_note` với paper ResNet: tool trả `needs_confirmation` trước khi người dùng đồng ý và `saved` sau câu trả lời “Yes”; bổ sung lệnh cài/chạy `cloudflared` trong `requirements.txt` dưới dạng comment, không phải dependency pip.

### Bằng chứng

- Commit: `4922ead` (baseline), `958065b` (thông tin nhóm và phân tích lỗi), `ea8b610` (unit tests), `a6871d0` (tool mới), `f291202` (transcript, ghi chú mẫu, hướng dẫn Cloudflare).
- Run baseline gốc nằm trong lịch sử Git: `git show 4922ead:starter_v0/runs/v0_B_base_openai_20261110T173129593859.json`; file này không còn trong cây thư mục hiện tại.
- File: `starter_v0/tools/save_note/tool.py`, `starter_v0/tools/save_note/TOOL.md`, `starter_v0/tests/test_tools_todo.py`; transcript `starter_v0/transcripts/v2_openai_20261110T193522228562.transcript.json`; ghi chú `starter_v0/notes/28828669400f44f6a0812485304d201e.json`.
- Kiểm tra lại toàn bộ suite khi hoàn thiện báo cáo: `.venv/bin/python -m pytest tests/ -q` từ `starter_v0/` — **92 passed**, không failed/skipped. Đây là kết quả suite chung hiện tại, không quy toàn bộ 92 test cho cá nhân.
- Báo cáo cá nhân: `report/team/2A202603974_KhongNgocAnh.md`.

## LyHaTranTran-2A202603968

### Phần việc phụ trách

- CP2: v3 (`system_prompt.md`) và v4 (`tools.yaml`), mỗi version một giả thuyết, có run base/group.
- CP5: transcript live chat v4, hoàn thiện group report.

### Đóng góp cụ thể

- v3: thay câu "just go ahead and do it" bằng quy ước `response_type` + xác nhận trước khi `send`; base 0.90 → 1.00.
- v4: viết lại description 11 tool (khi nào dùng/không dùng, convention args, boundary `send`/`save_note`); base 1.00, group 0.50 → 0.80.
- Chuẩn hoá `version_log.csv`, viết B1/B6 và hoàn thiện các mục còn trống của group report.

### Bằng chứng

- Commit `0cf7acc`; `starter_v0/runs/v3_B_base_openai_20261110T194744125722.json`, `starter_v0/runs/v4_B_base_openai_20261111T014227776599.json`, `starter_v0/runs/v4_B_group_openai_20261111T014254803430.json`; `starter_v0/transcripts/v4_openai_20261111T014329378074.transcript.json`.
- Báo cáo cá nhân: `report/team/2A202603968_LyHaTranTran.md`.

## VuongThuThao-2A202603966

### Phần việc phụ trách

- Đề xuất và thực hiện cải tiến `system_prompt.md` dựa trên kết quả đánh giá thực nghiệm.
- Xây dựng frontend cho hệ thống

### Đóng góp cụ thể

- Đề xuất giả thuyết loại bỏ việc tự suy đoán thông tin còn thiếu, yêu cầu người dùng bổ sung thông tin khi thiếu các tham số bắt buộc như account handle hoặc URL.
- Chỉnh sửa `system_prompt.md` để triển khai giả thuyết và tạo phiên bản v1.
- Xây dựng giao diện cho hệ thống

### Bằng chứng

- File/commit/PR:
  - `starter_v0/artifacts/system_prompt.md`: Nội dung system prompt được điều chỉnh ở v1
  - `starter_v0/app.py`: Giao diện của hệ thống
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng ChatGPT để hỗ trợ xây dựng giao diên, phân tích lỗi, đề xuất giả thuyết cải tiến và rà soát system prompt
  - Sử dụng Python, `run_eval.py` và OpenAI provider để thực hiện các thử nghiệm


