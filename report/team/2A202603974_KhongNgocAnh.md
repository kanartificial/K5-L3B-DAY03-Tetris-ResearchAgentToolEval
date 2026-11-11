# Báo cáo cá nhân — Khổng Ngọc Anh — 2A202603974

## 1. Thông tin thành viên

- Họ tên: Khổng Ngọc Anh
- MSSV: 2A202603974
- Email: 26ai.anhkn2@vinuni.edu.vn
- Nhóm / lớp: Tetris / L3B
- GitHub: `kanartificial`

## 2. Phần việc phụ trách

- **CP1:** chạy baseline bằng provider thật, ghi nhận kết quả và phân tích lỗi làm cơ sở cho nhóm tối ưu agent.
- **CP3:** phát triển tool mới `save_note`, đăng ký tool, viết tài liệu và unit test; hoàn thành các test skipped của tool có sẵn.
- **Hỗ trợ CP5:** thử nghiệm chat live, lưu transcript và file ghi chú mẫu; bổ sung hướng dẫn dùng Cloudflare Tunnel để hỗ trợ chia sẻ ứng dụng local.
- Khởi tạo thông tin nhóm trong `TEAM.md` và bổ sung phần baseline/failure analysis ban đầu vào báo cáo nhóm.

## 3. Đóng góp cụ thể

### 3.1. Baseline và phân tích lỗi

- Commit `4922ead` lưu run baseline `v0_B_base_openai_20261110T173129593859` bằng OpenAI / `gpt-4o-mini`: 15/20 case pass, `case_accuracy=0.75`, `tool_routing_accuracy=0.80`, `argument_accuracy=0.75`, `multiturn_accuracy=1.00`; không có case lỗi model provider.
- Commit `958065b` bổ sung phân tích 5 case FAIL: R08 gọi tool ngoài phạm vi, R10 đoán handle khi thiếu thông tin, R11 tự tạo URL, R12 gọi gửi trước xác nhận, R13 chọn đúng tool nhưng sai/thiếu arguments của `lookup`.
- Đề xuất hướng sửa tương ứng: hỏi lại thay vì đoán, xác nhận trước hành động và làm rõ convention `query`/`topic`. Phân biệt lỗi routing/arguments với lỗi HTTP của dịch vụ tool; pass eval không đồng nghĩa lấy dữ liệu thành công end-to-end.
- Run 0.75 trên là bằng chứng lịch sử trong commit `4922ead`, không còn là file trong cây thư mục hiện tại. `version_log.csv` hiện dùng một run baseline khác đạt 0.70; không dùng hai run này như cùng một phép đo hay nhận phần cải tiến v1–v4 của các thành viên khác.

### 3.2. Tool mới `save_note`

- Commit `a6871d0` thêm `tools/save_note/tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py` và khai báo schema trong `artifacts/tools.yaml`.
- Tool lưu `note_id`, `title`, `content`, `source_url` thành JSON UTF-8 tại `starter_v0/notes/<note_id>.json`; loại bỏ khoảng trắng ở đầu/cuối dữ liệu.
- Khi chưa xác nhận, tool trả `needs_confirmation` và không ghi file. Khi đã xác nhận, các trường dữ liệu phải là chuỗi không rỗng; lỗi dữ liệu/lưu trữ được trả về dưới dạng error dict.
- Tool chỉ lưu nội dung được truyền vào, không tự tải paper, kiểm chứng nguồn hay gửi Telegram. Description nêu rõ khi nào dùng, khi nào phải hỏi lại và chỉ đặt `confirmed=true` sau xác nhận rõ ràng.

### 3.3. Unit tests offline

- Commit `ea8b610` thay 14 test skipped của các tool có sẵn bằng kiểm tra thật theo mẫu `test_tools_examples.py`: clarify, format, send, lookup, fetch, timeline, social_search và policy.
- Dùng fixture `fake_http`, fake API keys và `monkeypatch`; không gọi mạng thật. Kiểm tra cả request gửi đi, ánh xạ response, giới hạn số item và ranh giới tin cậy của policy.
- Kiểm tra các biên `fetch` 3999/4000/4001 ký tự, hai kiểu tìm kiếm `Top`/`Latest`, dữ liệu format rỗng và policy query rỗng.
- Thêm 3 test `save_note` sử dụng *Attention Is All You Need* (`https://arxiv.org/pdf/1706.03762`): lưu đúng JSON và trim khoảng trắng; từ chối nội dung rỗng mà không tạo thư mục; trả lỗi khi đường dẫn lưu bị một file chặn.
- Test lưu ghi chú dùng `tmp_path`, không ghi vào thư mục notes thật. Kiểm tra lại suite chung khi hoàn thiện báo cáo bằng `.venv/bin/python -m pytest tests/ -q` từ `starter_v0/`: **92 passed, 0 failed, 0 skipped**. Đây là kết quả hiện tại của cả repo, không phải số test do riêng tôi viết.

### 3.4. Thử nghiệm live và hỗ trợ demo

- Commit `f291202` lưu các transcript thử chat và hai ghi chú ResNet mẫu. Transcript `v2_openai_20261110T193522228562` thể hiện tool trả `needs_confirmation` trước xác nhận, rồi trả `saved` sau khi người dùng trả lời “Yes”.
- Kết quả lưu có `note_id=28828669400f44f6a0812485304d201e`, đối chiếu được với file JSON trong `starter_v0/notes/`.
- Bổ sung hướng dẫn cài binary `cloudflared` cho Linux amd64 và lệnh tunnel tới `http://localhost:8501` trong comment của `requirements.txt`. `cloudflared` không phải dependency cài bằng pip; phần này là hỗ trợ vận hành, không phải đóng góp xây dựng frontend.
- Giới hạn bằng chứng: transcript ResNet trên chứng minh luồng xác nhận/lưu, không chứng minh model đã đọc paper hoặc kiểm chứng nội dung. Một số transcript OpenRouter ghi lỗi thiếu `OPENROUTER_API_KEY` hoặc không có lượt chat; không tính chúng là demo thành công. Commit hướng dẫn tunnel cũng không tự chứng minh một URL public đã hoạt động.

## 4. Bằng chứng

| Commit | Nội dung đối chiếu |
| --- | --- |
| `4922ead` — First commit + Cp1 | Run baseline đầu tiên và dòng version log |
| `958065b` — add group report | Thông tin nhóm, bảng baseline và phân tích 5 lỗi ban đầu |
| `ea8b610` — tools tests | Hoàn thành test skipped và 3 test của tool mới |
| `a6871d0` — tool | Implementation, tài liệu, đăng ký và schema `save_note` |
| `f291202` — add cloudflare | Transcript chat, notes mẫu và hướng dẫn cài/chạy tunnel |

Các file có thể kiểm tra trực tiếp từ báo cáo này:

- [Implementation save_note](../../starter_v0/tools/save_note/tool.py), [tài liệu tool](../../starter_v0/tools/save_note/TOOL.md).
- [Unit tests](../../starter_v0/tests/test_tools_todo.py), [tool registry](../../starter_v0/tools/__init__.py), [tool declarations](../../starter_v0/artifacts/tools.yaml).
- [Transcript xác nhận và lưu ResNet](../../starter_v0/transcripts/v2_openai_20261110T193522228562.transcript.json), [JSON đã lưu](../../starter_v0/notes/28828669400f44f6a0812485304d201e.json).
- [Hướng dẫn cloudflared trong requirements.txt](../../starter_v0/requirements.txt), [version log hiện tại](../../starter_v0/artifacts/version_log.csv).
- Run baseline lịch sử: xem bằng `git show 4922ead:starter_v0/runs/v0_B_base_openai_20261110T173129593859.json`; không tạo link tới một file đã không còn trong cây thư mục.

**AI/công cụ đã dùng và cách kiểm tra:**

- Sử dụng trợ lý AI hỗ trợ đọc code, phân tích kết quả, triển khai tool/test, hướng dẫn vận hành và soạn báo cáo; đối chiếu nội dung với commit, file JSON và kết quả chạy lệnh, không lấy câu trả lời AI làm bằng chứng thực nghiệm.
- Dùng Git để xác định phạm vi đóng góp theo tác giả `kana`; Python/pytest để kiểm tra tool offline; OpenAI / `gpt-4o-mini` để thử agent live; đọc transcript và notes để đối chiếu trạng thái thực thi.
- Phân biệt unit test của code tool với eval routing của model. Không nhận phần viết `eval_group.json` hoặc cải tiến prompt/frontend khi các commit trên không chứng minh đóng góp đó.

## 5. Tự đánh giá

- Hoàn thành phần nền tảng đánh giá ban đầu, tool lưu ghi chú và kiểm thử offline có cả happy path, bad input và storage failure. Các đóng góp có commit và file thực nghiệm để truy lại.
- Bài học chính: một lời trả lời “đã lưu” không đủ; phải đối chiếu kết quả tool và file JSON. Tương tự, eval routing pass không chứng minh dịch vụ bên ngoài hoạt động hay nội dung nghiên cứu đã được kiểm chứng.
- Điểm cần cải thiện: chất lượng nguồn của nội dung trước khi lưu, độ đầy đủ của regression coverage cho guardrail xác nhận và quản lý log thử nghiệm để không lẫn transcript rỗng/lỗi với bằng chứng demo. Tách rõ kết quả lịch sử của cá nhân với số liệu phiên bản cuối của nhóm.
