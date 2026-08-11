# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B05
- Repository URL: [github.com/kEeeE22/DAY13_2A202601117_DANGHOANGHAI.git](https://github.com/kEeeE22/DAY13_2A202601117_DANGHOANGHAI.git)
- Commit SHA cuối: 4c2ef24a489f84eb7852f8e1adeefe17f87e86af
- Thành viên và vai trò: Nhóm đã thực hiện các vai trò Logging, Tracing, Dashboard và Incident.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 27
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `submission/evidence/dashboard.html`

## 3. Logging và tracing

- Evidence correlation ID: Nộp kèm trong `submission/evidence/` (VD: `req-2a96c338` xuất hiện nhất quán xuyên suốt luồng xử lý).
- Evidence PII redaction: Nộp kèm trong `submission/evidence/` (user_id được băm thành hash như `867738e76862`, không lưu trữ raw string).
- Evidence trace waterfall: Xem ảnh trace waterfall trong thư mục evidence.
- Giải thích một span đáng chú ý: Span `retrieval` và `llm_call` chiếm phần lớn tổng thời gian, phản ánh trực tiếp nguyên nhân gây chậm khi hệ thống bị nghẽn (sự cố rag_slow).

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `v1` (label: `production`)
- Version/label candidate: `v2` (label: `staging`)
- Trace ID của mỗi version: Các trace được ghi nhận trong Langfuse.
- Bằng chứng đổi label hoặc rollback: Xem ảnh chụp màn hình UI Langfuse trong `submission/evidence/`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard.html` và `submission/evidence/dashboard-summary.json`.
- SLO đã chọn và lý do: latency P95 <= 3000 ms để bảo vệ trải nghiệm người dùng; error_rate_pct <= 2% để phát hiện lỗi hệ thống; total cost <= 2.5 USD để kiểm soát chi phí; quality_avg >= 0.75 để theo dõi chất lượng câu trả lời.
- Alert rules và runbook: Thành viên C cung cấp metric và dashboard; thành viên SRE/Alerts sẽ hoàn thiện `config/alert_rules.yaml` và `docs/alerts.md` dựa trên các SLO trên.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: Độ trễ (latency) P95 tăng vọt lên mức ~18.75 giây (hơn 18000ms) trên tính năng `refund`.
- Trace ID liên quan: `req-2a96c338`
- Log line/correlation ID liên quan: `req-2a96c338`
- Root cause: Bị tiêm sự cố `rag_slow`, gây ra hiện tượng nghẽn nặng ở thành phần Retrieval (truy xuất dữ liệu RAG), kéo dài thời gian phản hồi cho mọi request.
- Fix action: Xóa bỏ sự cố giả lập hoặc tối ưu lại hệ thống vector store, thêm caching cho RAG.
- Preventive measure: Đặt timeout rõ ràng (fail-fast) cho lệnh RAG retrieval thay vì để request bị treo mãi. Cấu hình alert khi P95 latency vượt ngưỡng báo cáo.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.


| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Thành viên A | CP1 Middleware, gán Correlation ID, và bổ sung exception handler (phần mở rộng). | TODO | Hiểu cách gán Correlation ID để dễ dàng tra cứu log. |
| Thành viên B | CP1 PII Scrubbing, regex patterns và kiểm chứng log không lộ PII. | TODO | Hiểu cách dùng regex để bảo vệ dữ liệu PII an toàn. |
| Thành viên C | CP1/CP2 đo đếm error_rate_pct và thiết kế spec Dashboard 6 nhóm chỉ số. | TODO | Biết cách biến log thành SLI/SLO để đọc triệu chứng trước khi mở trace/log. |
| Thành viên D | CP2 Thiết lập SLO, viết Alerts rules và Alert Runbook xử lý sự cố. | TODO | Hiểu cách thiết lập các cảnh báo dựa trên ngưỡng SLO. |
| Thành viên E | Chạy load test, bọc trace cho sub-component RAG/LLM, dẫn dắt điều tra Challenge và hoàn thiện báo cáo. | TODO | Cách ứng dụng Trace để truy vết lỗi đến tận gốc rễ (Root cause). |
