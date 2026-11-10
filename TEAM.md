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

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

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
