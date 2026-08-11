# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard.html` và `submission/evidence/dashboard-summary.json`.
- SLO đã chọn và lý do: latency P95 <= 3000 ms để bảo vệ trải nghiệm người dùng; error_rate_pct <= 2% để phát hiện lỗi hệ thống; total cost <= 2.5 USD để kiểm soát chi phí; quality_avg >= 0.75 để theo dõi chất lượng câu trả lời.
- Alert rules và runbook: Thành viên C cung cấp metric và dashboard; thành viên SRE/Alerts sẽ hoàn thiện `config/alert_rules.yaml` và `docs/alerts.md` dựa trên các SLO trên.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Thành viên C | Metrics & Dashboard: bổ sung `error_rate_pct`, xác minh 6 panel dashboard, tạo dashboard artifact từ `data/logs.jsonl` | TODO | Biết cách biến log thành SLI/SLO để đọc triệu chứng trước khi mở trace/log |
