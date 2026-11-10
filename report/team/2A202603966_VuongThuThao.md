# Báo cáo cá nhân — VuongThuThao-2A202603966.md

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Vương Thu Thảo
- MSSV: 2A202603966
- Email: 26ai.thaovt@vinuni.edu.vn

## 2. Phần việc phụ trách

- Đề xuất và thực hiện cải tiến `system_prompt.md` dựa trên kết quả đánh giá thực nghiệm.
- Xây dựng frontend cho hệ thống

## 3. Đóng góp cụ thể

- Đề xuất giả thuyết loại bỏ việc tự suy đoán thông tin còn thiếu, yêu cầu người dùng bổ sung thông tin khi thiếu các tham số bắt buộc như account handle hoặc URL.
- Chỉnh sửa `system_prompt.md` để triển khai giả thuyết và tạo phiên bản v1.
- Xây dựng giao diện cho hệ thống

## 4. Bằng chứng

- File/commit/PR:
  - `starter_v0/artifacts/system_prompt.md`: Nội dung system prompt được điều chỉnh ở v1
  - `starter_v0/app.py`: Giao diện của hệ thống
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng ChatGPT để hỗ trợ xây dựng giao diên, phân tích lỗi, đề xuất giả thuyết cải tiến và rà soát system prompt
  - Sử dụng Python, `run_eval.py` và OpenAI provider để thực hiện các thử nghiệm
  
## 5. Tự đánh giá

- Hoàn thành việc đánh giá baseline, xác định vấn đề và triển khai một giả thuyết cải tiến có thể kiểm chứng
- Biết cách sử dụng kết quả thực nghiệm để định hướng thay đổi thay vì chỉnh sửa system prompt theo cảm tính

